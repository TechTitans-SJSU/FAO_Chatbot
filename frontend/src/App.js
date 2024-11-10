import React from 'react';
import { ChakraProvider, Box, VStack, Heading } from '@chakra-ui/react';
import PDFUpload from './components/PDFUpload';
import ChatInterface from './components/ChatInterface';

const App = () => {
  return (
    <ChakraProvider>
      <Box minH="100vh" bg="gray.50" py={8}>
        <VStack spacing={8} w="full" maxW="container.lg" mx="auto">
          <Heading>PDF Chatbot</Heading>
          <PDFUpload />
          <ChatInterface />
        </VStack>
      </Box>
    </ChakraProvider>
  );
};

export default App;