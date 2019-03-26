package it.unibz.tsmodel.dao;

import java.sql.Timestamp;
import java.util.List;

import javax.persistence.EntityManager;
import javax.persistence.NoResultException;
import javax.persistence.PersistenceContext;
import javax.persistence.TypedQuery;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;

import it.unibz.tsmodel.domain.ParkingObservation;

@Repository
public class ParkingObservationDao {

	private final Log logger = LogFactory.getLog(ParkingObservationDao.class);


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

	public ParkingObservation findNewestObservationsByPlace(String parkingId) {
				String query = "SELECT (o) " +
                "FROM ParkingObservation o " +
                "WHERE o.parkingplace = :pid"+
                " ORDER BY o.timestamp desc";

		TypedQuery<ParkingObservation> typedQuery = entityManager.createQuery(query, ParkingObservation.class).setMaxResults(1);
		typedQuery.setParameter("pid", parkingId);
		ParkingObservation singleResult = null;
		try{
			singleResult = typedQuery.getSingleResult();
		}catch(NoResultException ex) {
			logger.debug("No entry for station with place id "+ parkingId);
		}
		return singleResult;
	}


}
