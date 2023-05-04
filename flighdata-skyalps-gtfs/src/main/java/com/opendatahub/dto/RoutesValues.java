package com.opendatahub.dto;
import java.net.URL;
import java.util.Objects;

import org.springframework.lang.NonNull;

import com.opendatahub.enumClasses.continous_drop_off;
import com.opendatahub.enumClasses.continous_pickup;
import com.opendatahub.enumClasses.route_color;
import com.opendatahub.enumClasses.route_type;

import java.io.Serializable;
import java.lang.String;
public class RoutesValues implements Serializable {

    private static final long serialVersionUID = 1L;
	@NonNull
	private String route_id; // read specification
	@NonNull
	private String route_short_name;
	@NonNull
	private int route_type;// default value 1100

	public String getRoute_id() {
		return route_id;
	}

	public void setRoute_id(String route_id) {
		this.route_id = route_id;
	}

	public String getRoute_short_name() {
		return route_short_name;
	}

	public void setRoute_short_name(String route_short_name) {
		this.route_short_name = route_short_name;
	}

	public int getRoute_type() {
		return route_type;
	}

	public void setRoute_type(int route_type) {
		this.route_type = route_type;
	}


	public RoutesValues() {
		// TODO Auto-generated constructor stub
	}

	public RoutesValues(String route_id, String route_short_name, int route_type) {
		super();
		this.route_id = route_id;
		this.route_short_name = route_short_name;
		this.route_type = route_type;
	}

	@Override
	public String toString() {
		return "RoutesValues [route_id=" + route_id + ", route_short_name=" + route_short_name + ", route_type="
				+ route_type + "]";
	}
	@Override
    public boolean equals(Object obj) {
        if (obj == this) {
            return true;
        }
        if (!(obj instanceof RoutesValues)) {
            return false;
        }
        RoutesValues other = (RoutesValues) obj;
        return Objects.equals(route_id, other.route_id)
                && Objects.equals(route_short_name, other.route_short_name)
                && Objects.equals(route_type, other.route_type);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(route_id, route_short_name, route_type);
    }


	
}
