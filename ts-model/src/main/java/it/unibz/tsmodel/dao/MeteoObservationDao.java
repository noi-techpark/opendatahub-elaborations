package it.unibz.tsmodel.dao;
import it.unibz.tsmodel.domain.MeteoObservation;

import java.sql.Timestamp;
import java.util.List;

import javax.persistence.EntityManager;
import javax.persistence.PersistenceContext;

import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;
/**
 * @author mreinstalder
 * persistence functions for {@link MeteoObservation} objects
 *
 */
@Repository
public class MeteoObservationDao {
	@PersistenceContext
	private EntityManager entityManager;
	
	
	
	/**
	 * @return the list of {@link MeteoObservation} present in the DB
	 * after the specified date
	 */
	public List<MeteoObservation> findObservations(Timestamp afterThat) {
		String query = "SELECT (o) " + "FROM MeteoObservation o "
				+ "WHERE o.timestamp > '" + afterThat + "'";
		return entityManager.createQuery(query, MeteoObservation.class)
				.getResultList();
	}
	
	/**
	 @return the list of {@link MeteoObservation} present in the DB
	 */
	public List<MeteoObservation> findAllMeteoObservationss() {
		 return entityManager.createQuery("SELECT o FROM MeteoObservation o", MeteoObservation.class).getResultList();
    }
	
	@Transactional
	public void persist(MeteoObservation observation) {
		entityManager.persist(observation);
	}

}
