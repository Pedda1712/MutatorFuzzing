import asyncio
import ollama
import time
import logging
import random

logger = logging.getLogger(__name__)

class ModelHorde:
    """Balance generation across multiple Ollama servers."""

    model_name: str
    """Ollama model name"""
    
    hosts: list[str]
    """URLs (http://host:port) of ollama instances."""

    average_time_to_respond: list[float]
    """Average time to respond of each model"""

    epsilon: float
    """Algorithm maintains an epsilon-greedy assignment strategy."""

    learning_rate: float
    """[0; 1] by how much does the average_time_to_respond get updated"""

    timeouts: list[float]
    """Request timeouts per host."""

    client: dict[str, ollama.AsyncClient]

    def __init__(self, model_name: str, hosts: list[str], timeouts: list[float],  epsilon: float = 0.1, learning_rate: float = 0.25, no_response_penalty: float = 60):
        """Initialize a model horde.

        Parameters:
        -----------
        model_name : str
          ollama model identifier
        hosts : list[str]
          list of ollama hosts
        timeouts : list[float]
          timeout per host
        epsilon: float
          Probability of randomly (instead of greedily) assigning a prompt to a server.
        learning_rate : float
          this class keeps track of the average response time of each host,
          and distributes requests accordingly.
          The average response time is essentially a noisy reward function,
          tracked with a learning rate.
          Example: a LR of 0.5 means that the newest response time makes up
          50% of the estimate, with all previous estimates making up the other
          50%.
        no_response_penalty: float
          how many seconds of response time to consider as penalty in no-response case
        """
        self.epsilon = epsilon
        self.model_name = model_name
        self.hosts = hosts
        self.timeouts = timeouts
        self.learning_rate = learning_rate
        self.no_response_penalty = no_response_penalty
        self.average_time_to_respond = []
        self.client = {}
        for host, timeout in zip(self.hosts, self.timeouts):
            self.client[host] = ollama.AsyncClient(host, timeout = timeout)
        self.loop = asyncio.new_event_loop()

    async def _sample_one(self, host: str, prompt: tuple[int, str], timeout: float, retries: int = 1, system_message: str | None = None) -> tuple[int, str] | None:
        for i in range(retries):
            try:
                messages = []
                if system_message is not None:
                    logger.info(f"Added system message {system_message}")
                    messages.append({
                        "role": "system",
                        "content": system_message
                    })
                messages.append({
                    "role": "user",
                    "content": prompt[1]
                })

                response = str((await self.client[host].chat(
                    model = self.model_name,
                    messages = messages
                )).message.content)

                return (prompt[0], response)
            except Exception as e:
                logger.warn(f"Ollama returned exception {e}, retrying {i + 1} of {retries}...")
                continue
        return None

    async def _sample_model(self, host: str, prompts: list[tuple[int, str]], timeout: float, retries: int = 1, system_message: str | None = None) -> tuple[list[tuple[int, str] | None], float]:
        start = time.time()
        awaitables = [self._sample_one(host, p, timeout, retries, system_message) for p in prompts]
        results = await asyncio.gather(*awaitables)
        end = time.time()
        taken = end - start
        return results, taken

    def _divide_requests(self, prompts: list[tuple[int,str]]) -> list[list[tuple[int, str]]]:
        accumulated_expected_costs: list[float] = [0.0] * len(self.hosts)
        divided_requests: list[list[tuple[int, str]]] = []
        for _ in range(len(self.hosts)):
            divided_requests.append([])
        for p_index, p in enumerate(prompts):
            chosen_host = 0
            chosen_host_cost = accumulated_expected_costs[chosen_host] + self.average_time_to_respond[chosen_host]
            for proposal_index, average_time in enumerate(self.average_time_to_respond):
                proposal_host_cost = average_time + accumulated_expected_costs[proposal_index]
                if proposal_host_cost < chosen_host_cost:
                    chosen_host = proposal_index
                    chosen_host_cost = proposal_host_cost
            accumulated_expected_costs[chosen_host] = chosen_host_cost
            if p_index != 0 and random.random() < self.epsilon:
                chosen_host = random.choice(list(range(len(self.hosts))))
            divided_requests[chosen_host].append(p)

        return divided_requests

    def _update_response_times(self, results: list[tuple[list[tuple[int, str] | None], float]]):
        for host_index, host_result in enumerate(results):

            if len(host_result[0]) == 0:
                continue
            
            time_per_request = host_result[1] / len(host_result[0])
            
            num_timeouts = sum([response is None for response in host_result[0]])

            if num_timeouts > 0:
                logger.info(f'There were {num_timeouts} timeouts for host {self.hosts[host_index]}, applying penalty ...')

            time_per_request += self.no_response_penalty * (num_timeouts / len(host_result[0])) 
            
            self.average_time_to_respond[host_index] = self.average_time_to_respond[host_index] * (1 - self.learning_rate) + self.learning_rate * time_per_request
        logger.info(f'Average response times after update: {[(hostname, self.average_time_to_respond[hostindex]) for hostindex, hostname in enumerate(self.hosts)]}')

    def _extract_remaining_prompts(self, remaining_prompts: list[tuple[int, str]], results: list[tuple[list[tuple[int, str] | None], float]]):
        result_prompts = []

        # too lazy rn for less shit solution
        for remaining_prompt in remaining_prompts:
            is_finished = False
            for host_result in results:
                for prompt_sent in host_result[0]:
                    if prompt_sent is None:
                        continue
                    if remaining_prompt[0] == prompt_sent[0]:
                        is_finished = True
                        break
            if not is_finished:
                result_prompts.append(remaining_prompt)
        return result_prompts
        
    def request(self, prompts: list[str], system_message: str | None = None) -> list[str]:
        """Divide requests among the horde and return the results.

        Parameters:
        -----------
        prompts : list[str]
          list of prompts
        """
        if len(self.average_time_to_respond) == 0:
            self.average_time_to_respond = [1/len(self.hosts)] * len(self.hosts)

        remaining_prompts = list(enumerate(prompts))
        outputs = [''] * len(prompts)

        while len(remaining_prompts) != 0:
            divided_requests = self._divide_requests(remaining_prompts)

            pending_requests = [self._sample_model(self.hosts[host_index], prompts, self.timeouts[host_index] * len(prompts), 1, system_message) for host_index, prompts in enumerate(divided_requests)]

            async def wait_for_requests():
                return await asyncio.gather(*pending_requests)


            asyncio.set_event_loop(self.loop)
            results = self.loop.run_until_complete(wait_for_requests())
            asyncio.set_event_loop(None)

            self._update_response_times(results)

            remaining_prompts = self._extract_remaining_prompts(remaining_prompts, results)

            flattened_results = [p for host_result in results for p in host_result[0]]
            for result_item in flattened_results:
                if result_item is None:
                    continue
                outputs[result_item[0]] = result_item[1]

        return outputs
