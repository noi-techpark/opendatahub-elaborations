package com.opendatahub.utils;

import java.io.InputStream;

import com.amazonaws.AmazonClientException;
import com.amazonaws.AmazonServiceException;
import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.amazonaws.services.s3.model.ObjectMetadata;
import com.amazonaws.services.s3.transfer.TransferManager;
import com.amazonaws.services.s3.transfer.TransferManagerBuilder;
import org.slf4j.LoggerFactory;
import org.slf4j.Logger;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

/**
 * To upload files to an S3 bucket
 */
@Component
public class S3FileUtil {

    private Logger logger = LoggerFactory.getLogger(S3FileUtil.class);

    @Value("${aws.access-key-id}")
    private String accessKeyId;

    @Value("${aws.bucket-name}")
    private String bucketName;

    @Value("${aws.access-secret-key}")
    private String accessSecretKey;

    /**
     * Uploads a fileInputStream to a S3 bucket
     *
     * @param fileInputStream
     * @param fileName
     * @param contentLength
     * @param lastModified
     * @throws AmazonServiceException
     * @throws AmazonClientException
     * @throws InterruptedException
     */
    public void uploadFile(InputStream fileInputStream, String fileName)
            throws AmazonServiceException, AmazonClientException, InterruptedException {

        logger.info("upload of file: {} to S3", fileName);

        BasicAWSCredentials awsCreds = new BasicAWSCredentials(accessKeyId, accessSecretKey);

        AmazonS3 amazonS3 = AmazonS3ClientBuilder
                .standard()
                .withCredentials(new AWSStaticCredentialsProvider(awsCreds))
                .withRegion(Regions.EU_WEST_1)
                .build();

        TransferManager transferManager = TransferManagerBuilder.standard()
                .withS3Client(amazonS3)
                .build();

        ObjectMetadata objectMetadata = new ObjectMetadata();
        // objectMetadata.setContentLength(contentLength);

        transferManager.upload(bucketName, fileName, fileInputStream, objectMetadata);

        logger.info("upload of file: {} to S3 done", fileName);
    }

}
