package it.bz.odh.elaborations.services;

import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Lazy;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClient.ResponseSpec;

import reactor.core.publisher.Flux;
@Lazy
@Component
public class ODHReaderClient{
    
    @Autowired
    protected WebClient ninja;
    private DateFormat dateFormatter = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS");
    
    
    public ResponseMapping getStationData(Date from, Date to) {
        ResponseSpec retrieve = ninja.get()
                .uri("/v2/flat/EnvironmentStation/*/" + dateFormatter.format(from) + "/" + dateFormatter.format(to)
                        + "?limit=-1&where=sactive.eq.true,sorigin.eq.a22-algorab")
                .retrieve();
        Flux<ResponseMapping> bodyToFlux = retrieve.bodyToFlux(ResponseMapping.class);
        ResponseMapping blockLast = bodyToFlux.blockLast();
        return blockLast;
    }
    public ResponseMapping getActiveStationIds() {
        return ninja.get()
                .uri("/v2/flat/EnvironmentStation?limit=-1&where=sactive.eq.true,sorigin.eq.a22-algorab&select=scode")
                .retrieve().bodyToFlux(ResponseMapping.class).blockLast();
    }
    
}
