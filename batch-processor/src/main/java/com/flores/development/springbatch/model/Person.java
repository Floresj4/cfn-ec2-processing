package com.flores.development.springbatch.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.NonNull;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class Person {

	@NonNull
	private String firstName;
	
	@NonNull
	private String lastName;
}
