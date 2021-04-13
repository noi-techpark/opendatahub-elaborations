package it.bz.odh.elaborations.services;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Lazy;
import org.springframework.stereotype.Component;

import it.bz.odh.dto.DataMapDto;
import it.bz.odh.dto.ProvenanceDto;
import it.bz.odh.dto.RecordDtoImpl;
import it.bz.odh.json.NonBlockingJSONPusher;

@Lazy
@Component
public class ODHWriterClient extends NonBlockingJSONPusher{

	@Value(value="${stationtype}")
	private String stationtype;


	@Value("${provenance_name}")
	private String provenanceName;
	@Value("${provenance_version}")
	private String provenanceVersion;
	
    @Value("${origin}")
    private String origin;

	@Override
	public String initIntegreenTypology() {
		return stationtype;
	}

	@Override
	public ProvenanceDto defineProvenance() {
		return new ProvenanceDto(null, provenanceName, provenanceVersion, origin);
	}
}
