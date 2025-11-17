/**
 * Error Boundary component for catching and handling React errors.
 *
 * Provides graceful error handling with fallback UI and error reporting.
 */

import { Component, ErrorInfo, ReactNode } from 'react';
import {
  Box,
  Text,
  Button,
  VStack,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Code,
} from '@chakra-ui/react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    // Update state so the next render will show the fallback UI
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Log error details for debugging
    console.error('ErrorBoundary caught an error:', error);
    console.error('Error component stack:', errorInfo.componentStack);

    // Update state with error details
    this.setState({
      error,
      errorInfo,
    });

    // TODO: Send error to logging service (e.g., Sentry, LogRocket)
    // reportErrorToService(error, errorInfo);
  }

  handleReset = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  handleReload = (): void => {
    window.location.reload();
  };

  render(): ReactNode {
    const { hasError, error, errorInfo } = this.state;
    const { children, fallback } = this.props;

    if (hasError) {
      // Custom fallback UI if provided
      if (fallback) {
        return fallback;
      }

      // Default fallback UI
      return (
        <Box p={8} maxW="800px" mx="auto">
          <Alert
            status="error"
            variant="subtle"
            flexDirection="column"
            alignItems="center"
            justifyContent="center"
            textAlign="center"
            minH="400px"
            borderRadius="lg"
          >
            <AlertIcon boxSize="40px" mr={0} />
            <AlertTitle mt={4} mb={1} fontSize="2xl">
              Something went wrong
            </AlertTitle>
            <AlertDescription maxW="lg" mt={2}>
              <VStack spacing={4}>
                <Text>
                  We encountered an unexpected error. This has been logged and we'll look into it.
                </Text>

                {error && (
                  <Box
                    w="100%"
                    p={4}
                    bg="red.50"
                    borderRadius="md"
                    borderLeft="4px"
                    borderColor="red.500"
                  >
                    <Text fontWeight="bold" mb={2} fontSize="sm" color="red.800">
                      Error Details:
                    </Text>
                    <Code display="block" whiteSpace="pre-wrap" p={3} fontSize="xs" bg="white">
                      {error.toString()}
                    </Code>
                  </Box>
                )}

                {process.env.NODE_ENV === 'development' && errorInfo && (
                  <Box
                    w="100%"
                    p={4}
                    bg="gray.50"
                    borderRadius="md"
                    maxH="200px"
                    overflowY="auto"
                  >
                    <Text fontWeight="bold" mb={2} fontSize="sm">
                      Component Stack:
                    </Text>
                    <Code display="block" whiteSpace="pre-wrap" fontSize="xs">
                      {errorInfo.componentStack}
                    </Code>
                  </Box>
                )}

                <VStack spacing={2} pt={4}>
                  <Button colorScheme="blue" onClick={this.handleReset} size="lg">
                    Try Again
                  </Button>
                  <Button variant="outline" onClick={this.handleReload}>
                    Reload Page
                  </Button>
                </VStack>
              </VStack>
            </AlertDescription>
          </Alert>
        </Box>
      );
    }

    return children;
  }
}
