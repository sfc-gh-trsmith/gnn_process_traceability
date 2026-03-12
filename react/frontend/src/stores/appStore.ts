import { create } from 'zustand';

interface AppState {
  selectedDefectType: string | null;
  sidebarCollapsed: boolean;
  connectionStatus: 'connected' | 'disconnected' | 'checking';
  connectionError: string | null;
  setSelectedDefectType: (type: string | null) => void;
  toggleSidebar: () => void;
  setConnectionStatus: (status: 'connected' | 'disconnected' | 'checking', error?: string | null) => void;
}

export const useAppStore = create<AppState>((set) => ({
  selectedDefectType: null,
  sidebarCollapsed: false,
  connectionStatus: 'checking',
  connectionError: null,
  setSelectedDefectType: (type) => set({ selectedDefectType: type }),
  toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
  setConnectionStatus: (status, error = null) => set({ connectionStatus: status, connectionError: error }),
}));
