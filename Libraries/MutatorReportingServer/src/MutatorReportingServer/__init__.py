import MutatorFuzzing as mf

from flask import Flask, Response, abort, request
from flask_socketio import SocketIO, emit
from typing import Callable, Dict
from enum import Enum
import threading
import json

class ReportingServer():

    class Status(Enum):
        GENERATING = 'Generating'
        SUMMARIZING = 'Summarizing'
        VALIDATING = 'Validating'
        CHECKING_COVERAGE = 'Checking Coverage'

    response_time_history: Dict[str, list[float]]
    sut_information: mf.Summarization.Context.SUTInformation
    summarization_pool: mf.ModelHorde
    generation_pool: mf.ModelHorde
    documenation_sources: list[mf.Summarization.Context.Urn]

    most_recent_status: tuple[Status, float] = (Status.SUMMARIZING, 0.0)

    def __init__(self, server_name: str, sut_information: mf.Summarization.Context.SUTInformation, summarization_pool: mf.ModelHorde, generation_pool: mf.ModelHorde, documentation_sources: list[mf.Summarization.Context.Urn], persistor: mf.Persistor):
        self.sut_information = sut_information
        self.summarization_pool = summarization_pool
        self.generation_pool = generation_pool
        self.documentation_sources = documentation_sources
        self.response_time_history = {}
        self.persistor = persistor
        
        self.app = Flask(server_name)
        self.app.add_url_rule('/sut-info', 'sut-info', self.sut_info)
        self.app.add_url_rule('/validation-results', 'validation-results', self.validation_results)
        self.app.add_url_rule('/coverage-results', 'coverage-results', self.coverage_results)
        self.app.add_url_rule('/response-times', 'response-times', self.response_times)
        self.app.add_url_rule('/generations', 'generations', self.generations)
        self.app.add_url_rule('/generation/<timestamp>', 'generation', self.generation)
        self.app.add_url_rule('/documentation-groups', 'documentation-groups', self.documentation_groups)
        self.app.add_url_rule('/documentation-group/<id>', 'documentation-group', self.documentation_group)
        self.app.after_request(self.allow_any_origin)
        self.app.debug = False
        self.socketio = SocketIO(self.app, cors_allowed_origins='*')

        self.socketio.on('status')(self.on_status_request)

    def allow_any_origin(self, response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

    def generation(self, timestamp):
        filecontent = self.persistor.fetch_single(timestamp)
        return {"content" : filecontent}

    def generations(self):
        page = request.args.get('page', default=0, type=int)
        size = request.args.get('size', default=10, type=int)
        results, number_of_pages = self.persistor.fetch_list(size, page)
        return {'numberOfPages': number_of_pages, 'currentPage': page, 'data': results}

    def documentation_groups(self):
        return {'data': [urn.get_semantic_name() for urn in self.documentation_sources]}

    def documentation_group(self, id):
        if int(id) < 0 or int(id) >= len(self.documentation_sources):
            abort(404, description='resource not found')
        return {'data': [[source.get_semantic_name(), source.get_cached_fetch().format()] for source in self.documentation_sources[int(id)].get_sources()]}

    def sut_info(self):
        return json.dumps({
            'sutType': self.sut_information.sut_type.value,
            'name': self.sut_information.name,
            'description': self.sut_information.description,
            'version': self.sut_information.version,
            'summarizationModelName': self.summarization_pool.model_name,
            'generationModelName': self.generation_pool.model_name
        })

    def response_times(self):
        return json.dumps(self.response_time_history)
    
    def validation_results(self):
        return json.dumps(dict(self.persistor.validity_report()))

    def coverage_results(self):
        coverage = self.persistor.get_coverage_history()
        return json.dumps({
            'coverage': [round(t[0]*100, 2) for t in coverage],
            'resummarizationEvents': [t[0] for t in self.persistor.get_resummarization()]
        })

    def on_status_request(self):
        emit('change-status', {'name': self.most_recent_status[0].value, 'data': self.most_recent_status[1]})

    def emit_status(self, status: Status, data: float = 0):
        self.most_recent_status = (status, data)
        self.socketio.emit('change-status', {'name': status.value, 'data' : data})

    def begin_generating(self, upto: int = 10) -> Callable[[],None]:
        num_generated = 0
        self.emit_status(ReportingServer.Status.GENERATING, 0)

        def generation_event():
            nonlocal num_generated
            num_generated += 1
            self.emit_status(ReportingServer.Status.GENERATING, round(num_generated / upto, 2))
            
        return generation_event
    
    def begin_validating(self, upto: int = 10) -> Callable[[],None]:
        num_generated = 0
        self.emit_status(ReportingServer.Status.VALIDATING, 0)

        def validation_event(event_name: str):
            nonlocal num_generated
            num_generated += 1
            self.emit_status(ReportingServer.Status.VALIDATING, round(num_generated / upto, 2))
            
        return validation_event

    def checking_coverage(self):
        self.emit_status(ReportingServer.Status.CHECKING_COVERAGE, 0)

    def begin_summarizing(self):
        self.emit_status(ReportingServer.Status.SUMMARIZING, 0)

    def submit_response_times(self):
        times: dict[str, float] = self.generation_pool.get_current_response_times()
        for host in times:
            if host not in self.response_time_history:
                self.response_time_history[host] = [times[host]]
            else:
                self.response_time_history[host].append(times[host])

    def submit_coverage(self, relative: float, absolute_count: int):
        self.persistor.submit_coverage(relative, absolute_count)

    def submit_resummarization(self):
        self.persistor.submit_resummarization()

    def submit_generation(self, validation_result: ValidationResult, prompt: str, raw_output: str, formatted_output: str):
        self.persistor.persist(validation_result, prompt, raw_output, formatted_output)

    def begin_epoch(self):
        self.persistor.bump_epoch()
        
    def validating(self, index, of):
        self.emit_status(ReportingServer.Status.VALIDATING, round(index/of, 2))
        
    def start(self):
        threading.Thread(target=lambda: self.app.run(debug=True, use_reloader=False)).start()
