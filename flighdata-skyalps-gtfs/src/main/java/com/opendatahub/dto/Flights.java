package it.noitechpark.dto;
import java.io.Serializable;
import java.util.Arrays;
import java.lang.String;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

@JsonIgnoreProperties(ignoreUnknown = true)
public class Flights implements Serializable {

	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	private String offset;
	private Data[] data;

	public Flights() {

	}

	public String getOffset() {
		return offset;
	}

	public void setOffset(String offset) {
		this.offset = offset;
	}

	public Data[] getData() {
		return data;
	}

	public void setData(Data[] data) {
		this.data = data;
	}

	public Flights(String offset, Data[] data) {
		super();
		this.offset = offset;
		this.data = data;
	}

	@Override
	public String toString() {
		return "Flights [offset=" + offset + ", data=" + Arrays.toString(data) + "]";
	}

}
