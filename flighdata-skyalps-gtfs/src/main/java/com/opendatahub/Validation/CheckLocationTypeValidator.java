package it.noiteachpark.Validation;

import java.util.Objects;

import javax.validation.ConstraintValidator;
import javax.validation.ConstraintValidatorContext;

import org.apache.logging.log4j.util.Strings;
import org.springframework.stereotype.Component;

import it.noitechpark.dto.StopsValue;
@Component
public class CheckLocationTypeValidator implements ConstraintValidator<CheckLocationType, String> {

	@Override
	public boolean isValid(String value, ConstraintValidatorContext context) {
		return Strings.isBlank(value);
				
	}
	
	public boolean checklocationtype(StopsValue value) {
		if(value.getLocation_type().getValue() == 1 || value.getLocation_type().getValue() == 0 || value.getLocation_type().getValue() == 2) {
	return true; 
	} else {
   return false;
	}
	}

}
