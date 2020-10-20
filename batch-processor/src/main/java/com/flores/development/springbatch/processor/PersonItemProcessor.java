package com.flores.development.springbatch.processor;

import org.springframework.batch.item.ItemProcessor;

import com.flores.development.springbatch.model.Person;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class PersonItemProcessor implements ItemProcessor<Person, Person> {

	@Override
	public Person process(final Person person) throws Exception {
		final String firstname = person.getFirstName().toUpperCase();
		final String lastname = person.getLastName().toUpperCase();
		
		final Person transformedPerson = new Person(firstname, lastname);
		log.info("Converted ({}) into ({})", person, transformedPerson);
		
		return transformedPerson;
	}
}
