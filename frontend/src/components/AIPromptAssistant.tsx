import { useState } from 'react';
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  Button,
  Textarea,
  VStack,
  Text,
  Box,
  HStack,
  Tag,
  Spinner,
  useToast,
} from '@chakra-ui/react';
import { StarIcon } from '@chakra-ui/icons';
import { getAIPromptSuggestions } from '../services/aiService';

interface AIPromptAssistantProps {
  isOpen: boolean;
  onClose: () => void;
  initialPrompt?: string;
  onApplySuggestion: (suggestion: string) => void;
}

export const AIPromptAssistant = ({
  isOpen,
  onClose,
  initialPrompt = '',
  onApplySuggestion,
}: AIPromptAssistantProps) => {
  const [prompt, setPrompt] = useState(initialPrompt);
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<{
    improvedPrompt: string;
    suggestions: string[];
    tags: string[];
  } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const toast = useToast();

  const handleGetSuggestions = async () => {
    if (!prompt.trim()) {
      toast({
        title: 'Error',
        description: 'Please enter a prompt first',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const result = await getAIPromptSuggestions(prompt);
      // Map the response to match the expected format
      setSuggestions({
        improvedPrompt: result.improved_prompt,
        suggestions: result.suggestions,
        tags: result.tags
      });
    } catch (err) {
      console.error('Error getting suggestions:', err);
      setError('Failed to get suggestions. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleApplySuggestion = () => {
    if (suggestions?.improvedPrompt) {
      onApplySuggestion(suggestions.improvedPrompt);
      onClose();
    }
  };

  return (
    <>
      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>AI Prompt Assistant</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={4} align="stretch">
              <Textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Enter your prompt here..."
                minH="100px"
                isDisabled={isLoading}
              />

              <Button
                colorScheme="purple"
                leftIcon={<StarIcon />}
                onClick={handleGetSuggestions}
                isLoading={isLoading}
                loadingText="Generating..."
                isDisabled={!prompt.trim()}
              >
                Get AI Suggestions
              </Button>

              {isLoading && <Spinner />}

              {error && (
                <Box color="red.500" mt={2}>
                  {error}
                </Box>
              )}

              {suggestions && !error && (
                <VStack align="stretch" spacing={4} mt={4}>
                  <Box>
                    <Text fontWeight="bold" mb={2}>
                      Improved Prompt:
                    </Text>
                    <Box
                      p={4}
                      borderWidth="1px"
                      borderRadius="md"
                      bg="gray.50"
                      whiteSpace="pre-wrap"
                    >
                      {suggestions.improvedPrompt}
                    </Box>
                  </Box>

                  {suggestions.suggestions.length > 0 && (
                    <Box>
                      <Text fontWeight="bold" mb={2}>
                        Suggestions for Improvement:
                      </Text>
                      <VStack align="stretch" spacing={2}>
                        {suggestions.suggestions.map((suggestion, index) => (
                          <Box
                            key={index}
                            p={3}
                            borderWidth="1px"
                            borderRadius="md"
                            bg="white"
                          >
                            {suggestion}
                          </Box>
                        ))}
                      </VStack>
                    </Box>
                  )}

                  {suggestions.tags.length > 0 && (
                    <Box>
                      <Text fontWeight="bold" mb={2}>
                        Suggested Tags:
                      </Text>
                      <HStack spacing={2} wrap="wrap">
                        {suggestions.tags.map((tag, index) => (
                          <Tag key={index} colorScheme="blue">
                            {tag}
                          </Tag>
                        ))}
                      </HStack>
                    </Box>
                  )}
                </VStack>
              )}
            </VStack>
          </ModalBody>

          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose}>
              Cancel
            </Button>
            <Button
              colorScheme="purple"
              onClick={handleApplySuggestion}
              isDisabled={!suggestions?.improvedPrompt}
            >
              Apply Suggestion
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  );
};

export default AIPromptAssistant;
