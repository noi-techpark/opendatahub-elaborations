package it.unibz.tsmodel.dao;



import it.unibz.tsmodel.domain.HolidayObservation;

import java.sql.Timestamp;
import java.util.List;

import javax.persistence.EntityManager;
import javax.persistence.PersistenceContext;

import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;
/**
 * @author mreinstalder
 * persistence functions for {@link HolidayObservation} objects
 *
 */
@Repository
public class HolidayObservationDao {
	@PersistenceContext
	private EntityManager entityManager;
	
	
	
	/**
	 * @return the list of {@link HolidayObservation} present in the DB
	 * after the specified date
	 */
	public List<HolidayObservation> findObservations(Timestamp afterThat) {
		String query = "SELECT (o) " + "FROM HolidayObservation o "
				+ "WHERE o.timestamp > '" + afterThat + "'";
		return entityManager.createQuery(query, HolidayObservation.class)
				.getResultList();
	}
	
	/**
	 * @return the list of {@link HolidayObservation} present in the DB
	 */
	public List<HolidayObservation> findAllHolidayObservations() {
		 return entityManager.createQuery("SELECT o FROM HolidayObservation o", HolidayObservation.class).getResultList();
    }
	
	/**
	 * @param holidayObservation the {@link HolidayObservation} to persist
	 */
	@Transactional
	public void persist(HolidayObservation holidayObservation) {
		entityManager.persist(holidayObservation);
	}

}
