import { ChakraProvider } from './components/ChakraProvider';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import PromptList from './pages/PromptList';
import PromptDetail from './pages/PromptDetail';
import PromptForm from './components/PromptForm';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
    },
  },
});

function App() {
  return (
    <ChakraProvider>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<MainLayout />}>
              <Route index element={<Navigate to="/prompts" replace />} />
              <Route path="prompts">
                <Route index element={<PromptList />} />
                <Route path="new" element={<PromptForm />} />
                <Route path=":id" element={<PromptDetail />} />
                <Route path=":id/edit" element={<PromptForm isEditing />} />
              </Route>
              {/* Add more routes as needed */}
              <Route path="*" element={<Navigate to="/prompts" replace />} />
            </Route>
          </Routes>
        </BrowserRouter>
        <ReactQueryDevtools initialIsOpen={false} />
      </QueryClientProvider>
    </ChakraProvider>
  );
}

export default App;
