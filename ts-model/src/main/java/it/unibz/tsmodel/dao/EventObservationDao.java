// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package it.unibz.tsmodel.dao;


import it.unibz.tsmodel.domain.EventObservation;

import java.sql.Timestamp;
import java.util.List;

import javax.persistence.EntityManager;
import javax.persistence.PersistenceContext;

import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;
/**
 * @author mreinstadler
 * persistence functions for {@link EventObservation} objects
 *
 */
@Repository
public class EventObservationDao {
	@PersistenceContext
	private EntityManager entityManager;
	
	
	
	/**
	 * @return the list of {@link EventObservation} present in the DB
	 * after the specified date
	 */
	public List<EventObservation> findObservations(Timestamp afterThat) {
		String query = "SELECT (o) " + "FROM EventObservation o "
				+ "WHERE o.timestamp > '" + afterThat + "'";
		return entityManager.createQuery(query, EventObservation.class)
				.getResultList();
	}
	
	/**
	 * @return the list of {@link EventObservation} present in the DB
	 */
	public List<EventObservation> findAllEventObservations() {
		 return entityManager.createQuery("SELECT o FROM EventObservation o", EventObservation.class).getResultList();
    }
	
	/**
	 * @param eventObservation the {@link EventObservation} to persist
	 */
	@Transactional
	public void persist(EventObservation eventObservation) {
		entityManager.persist(eventObservation);
	}

}
