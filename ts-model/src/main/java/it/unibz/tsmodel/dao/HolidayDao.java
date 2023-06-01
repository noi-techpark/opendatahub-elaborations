// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package it.unibz.tsmodel.dao;

import it.unibz.tsmodel.domain.Holiday;

import javax.persistence.EntityManager;
import javax.persistence.PersistenceContext;

import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;

/**
 * @author mreinstalder
 * persistence functions for {@link Holiday} objects
 * 
 */
@Repository
public class HolidayDao {
	@PersistenceContext
	private EntityManager entityManager;
	
	/**
	 * @param id
	 * @return the {@link Holiday} for the requested id
	 */
	public  Holiday findHoliday(int id) {
        return entityManager.find(Holiday.class, id);
    }
	
	 
	/**
	 * @param holiday the {@link Holiday} to store in the DB
	 */
	@Transactional
	public void persist(Holiday holiday) {
		entityManager.persist(holiday);
	}
}
