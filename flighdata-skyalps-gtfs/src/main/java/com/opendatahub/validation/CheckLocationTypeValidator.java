package com.opendatahub.Validation;

import java.util.Objects;

import javax.validation.ConstraintValidator;
import javax.validation.ConstraintValidatorContext;

import org.apache.logging.log4j.util.Strings;
import org.springframework.stereotype.Component;

import com.opendatahub.dto.StopsValue;
@Component
public class CheckLocationTypeValidator implements ConstraintValidator<CheckLocationType, String> {

	@Override
	public boolean isValid(String value, ConstraintValidatorContext context) {
		return Strings.isBlank(value);
				
	}

}
