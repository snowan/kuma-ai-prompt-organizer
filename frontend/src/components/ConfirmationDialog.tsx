import {
  AlertDialog,
  AlertDialogBody,
  AlertDialogContent,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogOverlay,
  Button,
  useDisclosure,
  UseDisclosureReturn,
} from '@chakra-ui/react';
import { useRef } from 'react';

interface ConfirmationDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmButtonText?: string;
  cancelButtonText?: string;
  confirmButtonColorScheme?: string;
  isLoading?: boolean;
}

const ConfirmationDialog = ({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmButtonText = 'Confirm',
  cancelButtonText = 'Cancel',
  confirmButtonColorScheme = 'blue',
  isLoading = false,
}: ConfirmationDialogProps) => {
  const cancelRef = useRef<HTMLButtonElement>(null);

  return (
    <AlertDialog
      isOpen={isOpen}
      leastDestructiveRef={cancelRef}
      onClose={onClose}
      isCentered
    >
      <AlertDialogOverlay>
        <AlertDialogContent>
          <AlertDialogHeader fontSize="lg" fontWeight="bold">
            {title}
          </AlertDialogHeader>

          <AlertDialogBody>{message}</AlertDialogBody>

          <AlertDialogFooter>
            <Button ref={cancelRef} onClick={onClose} isDisabled={isLoading}>
              {cancelButtonText}
            </Button>
            <Button
              colorScheme={confirmButtonColorScheme}
              onClick={onConfirm}
              ml={3}
              isLoading={isLoading}
            >
              {confirmButtonText}
            </Button>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialogOverlay>
    </AlertDialog>
  );
};

export default ConfirmationDialog;

// Hook version for easier usage in components
export const useConfirmationDialog = (): [UseDisclosureReturn, (config: Omit<ConfirmationDialogProps, 'isOpen' | 'onClose' | 'onConfirm'>) => Promise<boolean>] => {
  const disclosure = useDisclosure();
  const resolveRef = useRef<((value: boolean) => void) | null>(null);
  const dialogConfig = useRef<Omit<ConfirmationDialogProps, 'isOpen' | 'onClose' | 'onConfirm'>>({});

  const confirm = (config: Omit<ConfirmationDialogProps, 'isOpen' | 'onClose' | 'onConfirm'>) => {
    dialogConfig.current = config;
    disclosure.onOpen();
    return new Promise<boolean>((resolve) => {
      resolveRef.current = resolve;
    });
  };

  const handleClose = () => {
    if (resolveRef.current) {
      resolveRef.current(false);
      resolveRef.current = null;
    }
    disclosure.onClose();
  };

  const handleConfirm = () => {
    if (resolveRef.current) {
      resolveRef.current(true);
      resolveRef.current = null;
    }
    disclosure.onClose();
  };

  return [
    {
      ...disclosure,
      onClose: handleClose,
    },
    confirm,
  ];
};

export { AlertDialog, AlertDialogBody, AlertDialogFooter, AlertDialogHeader, AlertDialogOverlay };
