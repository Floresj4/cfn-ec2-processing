## cloudformation/

Contains the local testing and development cloudformation templates.  For Lambda execution the contents of these file must exist in a combination of S3 or Parameter Store.

### template.yml

The main cloudformation template for resource creation.

### params.yml

Params.yml is a configuration file used with the cloudformation client to substitute values that would have otherwise been manually entered via the AWS Cloudformation Wizard.  This file is loaded from the `./cloudformation` during local development.  The list of required parameters is found in the Parameters section of `./cloudformation/template.yml`.

params.yml is intentional excluded. See [/API_Parameter.html](https://docs.aws.amazon.com/AWSCloudFormation/latest/APIReference/API_Parameter.html) for more details
