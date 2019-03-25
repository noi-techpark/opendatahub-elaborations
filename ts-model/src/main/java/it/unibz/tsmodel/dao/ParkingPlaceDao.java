package it.unibz.tsmodel.dao;

import it.unibz.tsmodel.domain.ParkingPlace;

import java.util.List;

import javax.persistence.EntityManager;
import javax.persistence.PersistenceContext;

import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;

/**
 * persistence functions for {@link ParkingPlace} objects
 * @author mreinstalder
 * @author Patrick Bertolla
 */
@Repository
public class ParkingPlaceDao {

	@PersistenceContext
	private EntityManager entityManager;

//	/**
//	 * @param id
//	 * @return the {@link ParkingPlace} with the requested id
//	 */
//	public  ParkingPlace findParkingPlace(int id) {
//        return entityManager.find(ParkingPlace.class, id);
//    }

	/**
	 * @return the list of {@link ParkingPlace} present in the DB
	 */
	public List<ParkingPlace> findAllParkingPlaces() {
		 return entityManager.createQuery("SELECT o FROM ParkingPlace o", ParkingPlace.class).getResultList();
    }

	/**
	 * @param place the {@link ParkingPlace} to save in DB
	 */
	@Transactional
	public void persist(ParkingPlace place) {
		entityManager.persist(place);
	}

	/**
	 * update an existing parkingplace
	 * @param place entity to update/merge
	 */
	@Transactional
	public void merge(ParkingPlace place) {
		entityManager.merge(place);
	}
}
