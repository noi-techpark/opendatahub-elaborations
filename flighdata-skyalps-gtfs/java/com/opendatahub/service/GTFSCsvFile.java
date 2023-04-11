package com.opendatahub.service;

import java.io.DataInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.URL;
import java.net.URLConnection;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.junit.jupiter.api.Assertions;
import org.springframework.stereotype.Service;

import com.opencsv.CSVReader;
import com.opencsv.exceptions.CsvValidationException;
import com.opendatahub.constantsClasses.Stops;
import com.opendatahub.dto.StopsValue;

@Service
public class GTFSCsvFile {
	
	
	public static final File CSV_FILE = new File(new File(System.getProperty("user.home"), "Desktop"), "airports.csv");
	
	public static Map<String, ArrayList<String>> getCSVFile() throws IOException, CsvValidationException {
		Map<String, ArrayList<String>> multiValueMap = new HashMap<String, ArrayList<String>>();
		 File csv = CSV_FILE;
         boolean csvExists = csv.exists();
         if(csvExists == true) {
         	FileInputStream fis = new FileInputStream(csv); 
         	InputStreamReader isr = new InputStreamReader(fis, "UTF-8");
         	CSVReader reader = new CSVReader(isr);
         	String[] column; 
         	int lineNumber = 0;
         	while((column = reader.readNext()) != null) {
         		lineNumber++;
         		multiValueMap.put(column[13], new ArrayList<String>());
         		multiValueMap.get(column[13]).add(column[4]);
         		multiValueMap.get(column[13]).add(column[5]);
         		
         	}

         	reader.close();
         	isr.close();
         	fis.close();
         
         
         } else if (csvExists == false) {
         	URL url;
             URLConnection con;
             DataInputStream dis; 
             FileOutputStream fos; 
             byte[] fileData;  
             try {
                 url = new URL("https://cloud.opendatahub.com/index.php/s/nMCpGfE796Ct77X/download"); //File Location goes here
                 con = url.openConnection(); // open the url connection.
                 dis = new DataInputStream(con.getInputStream());
                 fileData = new byte[con.getContentLength()]; 
                 for (int q = 0; q < fileData.length; q++) { 
                     fileData[q] = dis.readByte();
                 }
                 dis.close(); // close the data input stream
                 fos = new FileOutputStream(new File(new File(System.getProperty("user.home"), "Desktop"), "airports.csv")); //FILE Save Location goes here
                 fos.write(fileData);  // write out the file we want to save.
                 fos.close(); // close the output stream writer
                 FileInputStream fis = new FileInputStream(csv); 
              	InputStreamReader isr = new InputStreamReader(fis, "UTF-8");
              	CSVReader reader = new CSVReader(isr);
              	String[] column; 
              	int lineNumber = 0;
              	while((column = reader.readNext()) != null) {
              		lineNumber++;
              		multiValueMap.put(column[13], new ArrayList<String>());
              		multiValueMap.get(column[13]).add(column[4]);
              		multiValueMap.get(column[13]).add(column[5]);
              		
              	}

              	reader.close();
              	isr.close();
              	fis.close();
             }
             catch(Exception m) {
                 System.out.println(m);
         }
         }
		return multiValueMap;
		
	}
	
	private static void CSVFile2() {
		// TODO Auto-generated method stub

	}
	
	public static void main(String[] args) throws IOException, CsvValidationException {
		getCSVFile();
	}

}
