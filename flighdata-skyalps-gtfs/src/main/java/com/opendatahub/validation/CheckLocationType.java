// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.opendatahub.validation;

import javax.validation.Constraint;

import javax.validation.Payload;

import org.springframework.context.annotation.Configuration;
import org.springframework.stereotype.Component;

import java.lang.annotation.Documented;
import java.lang.annotation.Retention;
import java.lang.annotation.Target;

import static java.lang.annotation.ElementType.FIELD;
import static java.lang.annotation.ElementType.METHOD;
import static java.lang.annotation.RetentionPolicy.RUNTIME;
@Documented
@Constraint(validatedBy = {CheckLocationTypeValidator.class})
@Retention(RUNTIME)
@Target(METHOD)
public @interface CheckLocationType {
	 String message() default "Error";
	    Class<?>[] groups() default {};
	    Class<? extends Payload>[] payload() default {};
}
