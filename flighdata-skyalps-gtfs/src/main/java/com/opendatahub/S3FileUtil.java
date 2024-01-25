// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.opendatahub;

import java.io.File;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import com.amazonaws.AmazonClientException;
import com.amazonaws.AmazonServiceException;
import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.amazonaws.services.s3.transfer.TransferManager;
import com.amazonaws.services.s3.transfer.TransferManagerBuilder;
import com.amazonaws.services.s3.transfer.Upload;

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
         * @param file.getName()
         * @param contentLength
         * @param lastModified
         * @throws AmazonServiceException
         * @throws AmazonClientException
         * @throws InterruptedException
         */
        public void uploadFile(File file)
                        throws AmazonServiceException, AmazonClientException, InterruptedException {

                logger.debug("upload of file: {} to S3", file.getName());

                BasicAWSCredentials awsCreds = new BasicAWSCredentials(accessKeyId, accessSecretKey);

                AmazonS3 amazonS3 = AmazonS3ClientBuilder
                                .standard()
                                .withCredentials(new AWSStaticCredentialsProvider(awsCreds))
                                .withRegion(Regions.EU_WEST_1)
                                .build();

                TransferManager transferManager = TransferManagerBuilder.standard()
                                .withS3Client(amazonS3)
                                .build();

                Upload upload = transferManager.upload(bucketName, file.getName(), file);
                upload.waitForCompletion();
                

                logger.debug("upload of file: {} to S3 done", file.getName());
        }

}