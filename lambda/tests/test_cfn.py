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
            self.assertEqual('floresj4-cfn-ec2-processing', bucket)
            self.assertEqual('batch-processor-0.0.1-SNAPSHOT.jar', key)


    '''
    handle a maven, semantic versioned, jar 
    '''
    def test_adjust_stack_name(self):
        bucket = 'bucket_name'
        key = 'some/artifact/uploaded.jar'

        name = cfn.get_name(key)
        namespace = cfn.get_namespace(bucket, key)
        self.assertEqual('uploaded', name)
        self.assertEqual('/bucket_name/some/artifact/', namespace)

        bucket = 'bucket_name'
        key = 'uploaded.jar'

        name = cfn.get_name(key)
        namespace = cfn.get_namespace(bucket, key)
        self.assertEqual('uploaded', name)
        self.assertEqual('/bucket_name/', namespace)


        bucket = '/bucket_name'
        key = '/uploaded.xyz'

        name = cfn.get_name(key)
        namespace = cfn.get_namespace(bucket, key)
        self.assertEqual('uploaded', name)
        self.assertEqual('/bucket_name/', namespace)


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