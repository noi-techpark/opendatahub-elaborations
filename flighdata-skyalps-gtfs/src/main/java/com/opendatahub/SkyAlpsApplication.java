package com.opendatahub;


import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;


@EnableScheduling
@SpringBootApplication
public class SkyAlpsApplication {

	public static void main(String[] args) {
        SpringApplication.run(SkyAlpsApplication.class, args);
    }

}