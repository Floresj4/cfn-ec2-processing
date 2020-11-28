import unittest
import sys
import json

from src import cfn

class TestCfn(unittest.TestCase):

    '''
    get relevant event info
    '''
    def test_get_event_info(self):

        with open('./lambda/tests/resources/s3-object-created.json', 'r') as file_obj:
            event_data = json.load(file_obj)

            bucket, key = cfn.get_event_info(event_data)
            self.assertEqual('example-bucket', bucket)
            self.assertEqual('test/key', key)

    '''
    handle a maven, semantic versioned, jar 
    '''
    def test_adjust_stack_name(self):
        stack_name, stack_namespace = cfn.stack_name_from_prefix('spring-batch-0.0.1-SNAPSHOT.jar')
        self.assertEqual('spring-batch-001-SNAPSHOT', stack_name)
        self.assertEqual('/', stack_namespace)

        stack_name, stack_namespace = cfn.stack_name_from_prefix('project-0.1.1.jar')
        self.assertEqual('project-011', stack_name)
        self.assertEqual('/', stack_namespace)

        stack_name, stack_namespace = cfn.stack_name_from_prefix('some/prefix/project-1.1.1.jar')
        self.assertEqual('project-111', stack_name)
        self.assertEqual('/some/prefix/', stack_namespace)

        stack_name, stack_namespace = cfn.stack_name_from_prefix('/project-1.1.2.jar')
        self.assertEqual('project-112', stack_name)
        self.assertEqual('/', stack_namespace)

    '''
    load the template body used in the CFN client 
    call.  The template.yaml should be tested through the
    wizard to minimize errors encountered through
    the client call
    '''
    def get_object_body(self):
        pass


    '''
    Load yaml parameters to be substituted into the template
    via the client call
    '''
    def get_object_as_yaml(self):
        pass


    '''
    Get the body of an object stored in S3.  Uniformly log the event.
    '''
    def get_s3_object_body(self):
        pass


    '''
    initialize a cloudformation client and make a request to
    create the stack/resources
    '''
    def create_stack(self):
        pass