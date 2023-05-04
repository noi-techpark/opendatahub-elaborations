package com.opendatahub.service;

import java.io.IOException;
import java.util.ArrayList;

import org.springframework.stereotype.Service;
@Service
public class GTFSRemoveDuplicates {
	public static <T> ArrayList<T> removeDuplicates(ArrayList<T> list) {
        ArrayList<T> newList = new ArrayList<T>();
        for (T element : list) {
            if (!newList.contains(element)) {
                newList.add(element);
            }
        }
        return newList;
    }
	
	public static void main(String[] args) throws IOException {
		removeDuplicates(null);
	}
}
