package com.flores.development.springbatch;

import java.util.Arrays;

import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

import lombok.extern.slf4j.Slf4j;

@Slf4j
@SpringBootApplication
public class Application implements ApplicationRunner {
	
	public static void main(String[] args) {
		SpringApplication.run(Application.class, args);
	}
	
	public void run(ApplicationArguments args) throws Exception {
		log.info("Application started with command-line arguments: {}", Arrays.toString(args.getSourceArgs()));
		log.info("NonOptionArgs: {}", args.getNonOptionArgs());
		log.info("OptionNames: {}", args.getOptionNames());

        for (String name : args.getOptionNames()){
        	log.info("arg-" + name + "=" + args.getOptionValues(name));
        }
	}
}
