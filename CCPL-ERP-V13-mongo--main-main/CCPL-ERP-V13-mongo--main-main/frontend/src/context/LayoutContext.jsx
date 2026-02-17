import { createContext, useState, useContext } from 'react'

const LayoutContext = createContext(null)

export const LayoutProvider = ({ children }) => {
  const [title, setTitle] = useState('Inventory ERP')

  return (
    <LayoutContext.Provider value={{ title, setTitle }}>
      {children}
    </LayoutContext.Provider>
  )
}

export const useLayout = () => {
  const context = useContext(LayoutContext)
  if (!context) {
    throw new Error('useLayout must be used within a LayoutProvider')
  }
  return context
}
