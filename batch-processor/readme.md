# batch-processor

A simple spring-batch project to develop and test this automation.

### Commandline Execution

Within this project space the sample batch-processor application be created and run with the following commands &ndash; from the application directory.

- Build - `mvn clean package`
- Run - `java -jar batch-...jar --datafile-path=..\sample-data.cs`

`batch-...` indicates the version or `mvn` build.finalname has been changed since the time of this writting.

Properties of the application can be found in `application.properties` or in the Spring `@ConfigurationProperties` bean.

### data/

A data file to run through the batch processing project.  This file will be pulled from AWS S3 when the EC2 instance initializes and starts the process.

### src/

Java source code here.

### pom.xml

Project dependency descriptor.