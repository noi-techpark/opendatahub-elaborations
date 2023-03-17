package it.noitechpark.dto;
import java.io.Serializable;
import java.lang.String;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

@JsonIgnoreProperties(ignoreUnknown = false)
public class fares implements Serializable {
	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	private SKY_GO SKY_GO;
	private SKY_PLUS SKY_PLUS;
	private SKY_BASIC SKY_BASIC;
	private SKY_LIGHT SKY_LIGHT;

	public fares() {

	}
	

	public fares(it.noitechpark.dto.SKY_GO SKY_GO, it.noitechpark.dto.SKY_PLUS SKY_PLUS,
			it.noitechpark.dto.SKY_BASIC SKY_BASIC, it.noitechpark.dto.SKY_LIGHT SKY_LIGHT) {
		super();
		this.SKY_GO = SKY_GO;
		this.SKY_PLUS = SKY_PLUS;
		this.SKY_BASIC = SKY_BASIC;
		this.SKY_LIGHT = SKY_LIGHT;
	}

@JsonProperty("SKY_GO")
	public SKY_GO getSKY_GO() {
		return SKY_GO;
	}

@JsonProperty("SKY_GO")
	public void setSKY_GO(SKY_GO SKY_GO) {
		this.SKY_GO = SKY_GO;
	}

@JsonProperty("SKY_PLUS")
	public SKY_PLUS getSKY_PLUS() {
		return SKY_PLUS;
	}

@JsonProperty("SKY_PLUS")
	public void setSKY_PLUS(SKY_PLUS SKY_PLUS) {
		this.SKY_PLUS = SKY_PLUS;
	}

@JsonProperty("SKY_BASIC")
	public SKY_BASIC getSKY_BASIC() {
		return SKY_BASIC;
	}

@JsonProperty("SKY_BASIC")
	public void setSKY_BASIC(SKY_BASIC SKY_BASIC) {
		this.SKY_BASIC = SKY_BASIC;
	}

@JsonProperty("SKY_LIGHT")
	public SKY_LIGHT getSKY_LIGHT() {
		return SKY_LIGHT;
	}

@JsonProperty("SKY_LIGHT")
	public void setSKY_LIGHT(SKY_LIGHT SKY_LIGHT) {
		this.SKY_LIGHT = SKY_LIGHT;
	}


	@Override
	public String toString() {
		return "fares [SKY_GO=" + SKY_GO + ", SKY_PLUS=" + SKY_PLUS + ", SKY_BASIC=" + SKY_BASIC + ", SKY_LIGHT="
				+ SKY_LIGHT + "]";
	}
	
	

}
