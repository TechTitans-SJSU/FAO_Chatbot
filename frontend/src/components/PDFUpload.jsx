import React, { useState } from 'react';
import { Flex } from '@chakra-ui/react';
import { 
  Box, 
  Button, 
  VStack, 
  Text, 
  useToast,
  Progress,
  Icon
} from '@chakra-ui/react';
import { FileUp, Check } from 'lucide-react';

const PDFUpload = () => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const toast = useToast();

  const handleFileUpload = async (event) => {
    const files = Array.from(event.target.files);
    
    for (const file of files) {
      if (file.type !== 'application/pdf') {
        toast({
          title: 'Invalid file type',
          description: 'Please upload PDF files only',
          status: 'error',
          duration: 3000,
          isClosable: true,
        });
        return;
      }

      setIsUploading(true);
      const formData = new FormData();
      formData.append('file', file);

      try {
        // Simulate upload progress
        const progressInterval = setInterval(() => {
          setUploadProgress(prev => {
            if (prev >= 90) {
              clearInterval(progressInterval);
              return 90;
            }
            return prev + 10;
          });
        }, 500);

        // Add error handling and logging
        console.log('Uploading file:', file.name);
        
        const response = await fetch('http://localhost:8000/api/upload', {
          method: 'POST',
          body: formData,
          // Add these headers
          headers: {
            'Accept': 'application/json',
            // Don't set Content-Type with FormData, browser will set it automatically
          },
        });

        clearInterval(progressInterval);
        setUploadProgress(100);

        if (!response.ok) {
          const errorData = await response.json().catch(() => null);
          console.error('Upload failed:', errorData);
          throw new Error(errorData?.message || 'Upload failed');
        }

        const responseData = await response.json();
        console.log('Upload successful:', responseData);

        setUploadedFiles(prev => [...prev, file.name]);
        toast({
          title: 'Upload successful',
          description: 'PDF has been processed successfully',
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
      } catch (error) {
        console.error('Upload error:', error);
        toast({
          title: 'Upload failed',
          description: error.message || 'There was an error uploading the file',
          status: 'error',
          duration: 3000,
          isClosable: true,
        });
      } finally {
        setIsUploading(false);
        setUploadProgress(0);
      }
    }
  };

  return (
    <Box p={6} borderWidth={1} borderRadius="lg" bg="white">
      <VStack spacing={4} align="stretch">
        <Button
          as="label"
          htmlFor="file-upload"
          cursor="pointer"
          colorScheme="blue"
          leftIcon={<Icon as={FileUp} />}
          isLoading={isUploading}
        >
          Upload PDF
          <input
            id="file-upload"
            type="file"
            accept=".pdf"
            multiple
            onChange={handleFileUpload}
            style={{ display: 'none' }}
          />
        </Button>

        {isUploading && (
          <Box>
            <Text mb={2}>Uploading...</Text>
            <Progress value={uploadProgress} size="sm" colorScheme="blue" />
          </Box>
        )}

        {uploadedFiles.length > 0 && (
          <Box>
            <Text mb={2} fontWeight="bold">Uploaded Files:</Text>
            <VStack align="stretch" spacing={2}>
              {uploadedFiles.map((filename, index) => (
                <Flex key={index} align="center" gap={2}>
                  <Icon as={Check} color="green.500" />
                  <Text>{filename}</Text>
                </Flex>
              ))}
            </VStack>
          </Box>
        )}
      </VStack>
    </Box>
  );
};

export default PDFUpload;