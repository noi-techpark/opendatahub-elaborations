// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.opendatahub.validation;

import javax.validation.ConstraintValidator;
import javax.validation.ConstraintValidatorContext;

import org.springframework.beans.BeanUtils;

public class ConditionalValidator implements ConstraintValidator<ConditionalValid, Object> {

	@Override
	public void initialize(ConditionalValid constraintAnnotation) {
		String field = constraintAnnotation.field();
		String dependentField = constraintAnnotation.dependentField();
		ConstraintValidator.super.initialize(constraintAnnotation);
	}
	
	@Override
	public boolean isValid(Object value, ConstraintValidatorContext context) {
		return false;
	}

}
