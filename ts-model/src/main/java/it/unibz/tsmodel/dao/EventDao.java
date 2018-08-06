package it.unibz.tsmodel.dao;
import it.unibz.tsmodel.domain.Event;

import javax.persistence.EntityManager;
import javax.persistence.PersistenceContext;

import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;

/**
 * @author mreinstalder
 * persistence functions for {@link Event} objects
 *
 */
@Repository
public class EventDao {

	@PersistenceContext
	private EntityManager entityManager;
	
	/**
	 * @param id
	 * @return the {@link Event} for the requested id
	 */
	public  Event findEvent(int id) {
        return entityManager.find(Event.class, id);
    }
	
	 
	/**
	 * @param event the {@link Event} to persist
	 */
	@Transactional
	public void persist(Event event) {
		entityManager.persist(event);
	}
}
