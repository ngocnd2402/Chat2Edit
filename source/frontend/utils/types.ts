export interface ImageInfo {
  index: number;
  base64_string: string;
}

export interface MediaModalProps {
  isOpen: boolean;
  onClose: () => void;
  src: string | null;
}

export interface Message {
  id: number;
  text: string;
  media: string[] | null;
  isLoading: boolean;
}

export interface SendMessageResponse {
  status: 'success' | 'error';
  result?: string[];
}