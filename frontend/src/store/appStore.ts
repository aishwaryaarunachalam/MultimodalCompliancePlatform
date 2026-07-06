import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AppStore {
  selectedDocId:   string | null;
  reviewerName:    string;
  sidebarOpen:     boolean;
  setSelectedDoc:  (id: string | null) => void;
  setReviewerName: (name: string) => void;
  toggleSidebar:   () => void;
}

export const useAppStore = create<AppStore>()(
  persist(
    (set) => ({
      selectedDocId:   null,
      reviewerName:    '',
      sidebarOpen:     true,
      setSelectedDoc:  (id)   => set({ selectedDocId: id }),
      setReviewerName: (name) => set({ reviewerName: name }),
      toggleSidebar:   ()     => set(s => ({ sidebarOpen: !s.sidebarOpen })),
    }),
    { name: 'compliance-app-store', partialize: (s) => ({ reviewerName: s.reviewerName }) }
  )
);
