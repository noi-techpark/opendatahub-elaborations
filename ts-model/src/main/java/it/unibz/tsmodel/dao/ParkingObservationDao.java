package it.unibz.tsmodel.dao;

import it.unibz.tsmodel.domain.ParkingObservation;

import java.sql.Timestamp;
import java.util.List;

import javax.persistence.EntityManager;
import javax.persistence.PersistenceContext;
import javax.persistence.TypedQuery;

import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;

@Repository
public class ParkingObservationDao {
	
	@PersistenceContext
	private EntityManager entityManager;
	
	/**
	 *@return the list of {@link ParkingObservation} with the specified parking id and after 
	 *the specified date present in the DB
	 */
	public List<ParkingObservation> findObservationsByPlace(String pid, Timestamp afterThat) {
		String query = "SELECT (o) " + 
                "FROM ParkingObservation o " + 
                "WHERE o.parkingplace = :pid AND o.timestamp > :afterThat"+
                " ORDER BY timestamp";
		
		TypedQuery<ParkingObservation> typedQuery = entityManager.createQuery(query, ParkingObservation.class);
		typedQuery.setParameter("pid", pid);
		typedQuery.setParameter("afterThat", afterThat);
		return  typedQuery.getResultList();
   }
	
	@Transactional
	public void persist(ParkingObservation observation) {
		entityManager.persist(observation);
	}


}
