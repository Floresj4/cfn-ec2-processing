package com.flores.development.springbatch.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.lang.NonNull;
import org.springframework.stereotype.Component;

import lombok.Getter;

@Component
@ConfigurationProperties
public class BatchConfigProperties {

    @NonNull
    @Getter
	@Value("${datafile-path}")
    private String datafilePath;
    
    @Getter
    @Value("${chunkSize:10}")
    private int chunkSize;
}