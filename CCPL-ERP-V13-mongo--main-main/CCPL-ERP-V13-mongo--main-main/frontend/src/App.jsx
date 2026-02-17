import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from './context/AuthContext'
import { LayoutProvider } from './context/LayoutContext'
import { useAuth } from './hooks/useAuth'
import MainLayout from './components/layout/MainLayout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import ProductsList from './pages/products/ProductsList'
import InventoryList from './pages/inventory/InventoryList'
import SuppliersList from './pages/suppliers/SuppliersList'
import ItemMaster from './pages/ItemMaster'
import ItemCategory from './pages/ItemCategory'
import ItemCategoryMaster from './pages/ItemCategoryMaster'
import VariantMaster from './pages/VariantMaster'
import SpecificationsManager from './pages/SpecificationsManager'
import PurchaseOrderList from './pages/PurchaseOrderList'
import PurchaseOrderForm from './pages/PurchaseOrderForm'
import PurchaseOrderDetail from './pages/PurchaseOrderDetail'
import BrandMaster from './pages/Masters/BrandMaster'
import SupplierMaster from './pages/Masters/SupplierMaster'
import FileManager from './pages/FileManager'
import WorkInProgress from './components/common/WorkInProgress'
import { BOMEditor, BOMViewer, BOMPool, BOMAllocator, DyeingPlans } from './pages/bom'

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()
  
  if (loading) return <div className="flex items-center justify-center h-screen">Loading...</div>
  if (!user) return <Navigate to="/login" />
  
  return children
}

function App() {
  return (
    <AuthProvider>
      <LayoutProvider>
        <BrowserRouter>
          <Routes>
          <Route path="/login" element={<Login />} />
          
          <Route element={<MainLayout />}>
            <Route path="/" element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } />
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } />
            <Route path="/products" element={
              <ProtectedRoute>
                <ProductsList />
              </ProtectedRoute>
            } />
            <Route path="/inventory" element={
              <ProtectedRoute>
                <InventoryList />
              </ProtectedRoute>
            } />
            <Route path="/suppliers" element={
              <ProtectedRoute>
                <SuppliersList />
              </ProtectedRoute>
            } />
            <Route path="/item-master" element={
              <ProtectedRoute>
                <ItemMaster />
              </ProtectedRoute>
            } />
            <Route path="/item-category" element={
              <ProtectedRoute>
                <ItemCategory />
              </ProtectedRoute>
            } />
            <Route path="/item-categories" element={
              <ProtectedRoute>
                <ItemCategoryMaster />
              </ProtectedRoute>
            } />
            <Route path="/variant-master" element={
              <ProtectedRoute>
                <VariantMaster />
              </ProtectedRoute>
            } />
            <Route path="/masters/brands" element={
              <ProtectedRoute>
                <BrandMaster />
              </ProtectedRoute>
            } />
            <Route path="/masters/suppliers" element={
              <ProtectedRoute>
                <SupplierMaster />
              </ProtectedRoute>
            } />
            <Route path="/specifications" element={
              <ProtectedRoute>
                <SpecificationsManager />
              </ProtectedRoute>
            } />
            <Route path="/file-manager" element={
              <ProtectedRoute>
                <FileManager />
              </ProtectedRoute>
            } />
            <Route path="/purchase-orders" element={
              <ProtectedRoute>
                <PurchaseOrderList />
              </ProtectedRoute>
            } />
            <Route path="/purchase-orders/create" element={
              <ProtectedRoute>
                <PurchaseOrderForm />
              </ProtectedRoute>
            } />
            <Route path="/purchase-orders/:poNumber/edit" element={
              <ProtectedRoute>
                <PurchaseOrderForm />
              </ProtectedRoute>
            } />
            <Route path="/purchase-orders/:poNumber" element={
              <ProtectedRoute>
                <PurchaseOrderDetail />
              </ProtectedRoute>
            } />
            
            {/* Dyeing BOM */}
            <Route path="/bom/editor" element={
              <ProtectedRoute>
                <BOMEditor />
              </ProtectedRoute>
            } />
            <Route path="/bom/view/:uid" element={
              <ProtectedRoute>
                <BOMViewer />
              </ProtectedRoute>
            } />
            <Route path="/bom/pool" element={
              <ProtectedRoute>
                <BOMPool />
              </ProtectedRoute>
            } />
            <Route path="/bom/allocate" element={
              <ProtectedRoute>
                <BOMAllocator />
              </ProtectedRoute>
            } />
            <Route path="/bom/plans" element={
              <ProtectedRoute>
                <DyeingPlans />
              </ProtectedRoute>
            } />

            {/* Masters - Work in Progress */}
            <Route path="/fabric-category" element={
              <ProtectedRoute>
                <WorkInProgress title="Fabric Category" description="Manage fabric categories and types for your inventory items." />
              </ProtectedRoute>
            } />
            <Route path="/warehouse-master" element={
              <ProtectedRoute>
                <WorkInProgress title="Warehouse Master" description="Configure and manage warehouse locations and storage facilities." />
              </ProtectedRoute>
            } />
            <Route path="/bin-location-master" element={
              <ProtectedRoute>
                <WorkInProgress title="BIN / Location Master" description="Define bin locations and storage positions within warehouses." />
              </ProtectedRoute>
            } />
            <Route path="/tax-hsn-master" element={
              <ProtectedRoute>
                <WorkInProgress title="Tax / HSN Master" description="Manage tax rates and HSN codes for compliance." />
              </ProtectedRoute>
            } />

            {/* Purchase - Work in Progress */}
            <Route path="/goods-receipt" element={
              <ProtectedRoute>
                <WorkInProgress title="Goods Receipt" description="Record and track incoming goods from purchase orders." />
              </ProtectedRoute>
            } />
            <Route path="/purchase-returns" element={
              <ProtectedRoute>
                <WorkInProgress title="Purchase Returns" description="Process returns to suppliers for defective or incorrect items." />
              </ProtectedRoute>
            } />
            <Route path="/vendor-bills" element={
              <ProtectedRoute>
                <WorkInProgress title="Vendor Bills" description="Manage and track bills received from vendors." />
              </ProtectedRoute>
            } />
            <Route path="/purchase-reports" element={
              <ProtectedRoute>
                <WorkInProgress title="Purchase Reports" description="View detailed analytics and reports on purchasing activities." />
              </ProtectedRoute>
            } />

            {/* Quality - Work in Progress */}
            <Route path="/quality-checks" element={
              <ProtectedRoute>
                <WorkInProgress title="Quality Checks" description="Define and manage quality check procedures and standards." />
              </ProtectedRoute>
            } />
            <Route path="/inspections" element={
              <ProtectedRoute>
                <WorkInProgress title="Inspections" description="Schedule and track quality inspections for incoming goods." />
              </ProtectedRoute>
            } />
            <Route path="/defects" element={
              <ProtectedRoute>
                <WorkInProgress title="Defects Management" description="Track, categorize, and resolve product defects." />
              </ProtectedRoute>
            } />
            <Route path="/quality-reports" element={
              <ProtectedRoute>
                <WorkInProgress title="Quality Reports" description="Generate reports on quality metrics and trends." />
              </ProtectedRoute>
            } />

            {/* Inventory Transactions - Work in Progress */}
            <Route path="/stock-movements" element={
              <ProtectedRoute>
                <WorkInProgress title="Stock Movements" description="Track all stock movements across warehouses and locations." />
              </ProtectedRoute>
            } />
            <Route path="/stock-adjustments" element={
              <ProtectedRoute>
                <WorkInProgress title="Stock Adjustments" description="Make inventory adjustments for discrepancies and corrections." />
              </ProtectedRoute>
            } />
            <Route path="/stock-transfers" element={
              <ProtectedRoute>
                <WorkInProgress title="Stock Transfers" description="Transfer inventory between warehouses and locations." />
              </ProtectedRoute>
            } />
            <Route path="/stock-issue" element={
              <ProtectedRoute>
                <WorkInProgress title="Stock Issue" description="Issue stock for production or internal consumption." />
              </ProtectedRoute>
            } />
            <Route path="/stock-levels" element={
              <ProtectedRoute>
                <WorkInProgress title="Stock Levels" description="View current stock levels across all locations." />
              </ProtectedRoute>
            } />

            {/* Reports - Work in Progress */}
            <Route path="/inventory-reports" element={
              <ProtectedRoute>
                <WorkInProgress title="Inventory Reports" description="Comprehensive reports on inventory status and valuation." />
              </ProtectedRoute>
            } />
            <Route path="/sales-reports" element={
              <ProtectedRoute>
                <WorkInProgress title="Sales Reports" description="Analyze sales performance and trends." />
              </ProtectedRoute>
            } />
            <Route path="/stock-summary" element={
              <ProtectedRoute>
                <WorkInProgress title="Stock Summary" description="Overview of stock status across all categories." />
              </ProtectedRoute>
            } />
            <Route path="/aging-analysis" element={
              <ProtectedRoute>
                <WorkInProgress title="Aging Analysis" description="Analyze inventory aging and identify slow-moving items." />
              </ProtectedRoute>
            } />

            {/* Settings - Work in Progress */}
            <Route path="/users" element={
              <ProtectedRoute>
                <WorkInProgress title="User Management" description="Manage user accounts, permissions, and access control." />
              </ProtectedRoute>
            } />
            <Route path="/roles" element={
              <ProtectedRoute>
                <WorkInProgress title="Role Management" description="Define and manage user roles and permissions." />
              </ProtectedRoute>
            } />
            <Route path="/company" element={
              <ProtectedRoute>
                <WorkInProgress title="Company Settings" description="Configure company profile and business settings." />
              </ProtectedRoute>
            } />
            <Route path="/email-config" element={
              <ProtectedRoute>
                <WorkInProgress title="Email Configuration" description="Set up email templates and notification settings." />
              </ProtectedRoute>
            } />
            <Route path="/general-settings" element={
              <ProtectedRoute>
                <WorkInProgress title="General Settings" description="Configure system-wide preferences and defaults." />
              </ProtectedRoute>
            } />

            {/* Catch-all for any undefined routes */}
            <Route path="*" element={
              <ProtectedRoute>
                <WorkInProgress title="Page Not Found" description="The page you're looking for doesn't exist or is still under development." />
              </ProtectedRoute>
            } />
          </Route>
        </Routes>
        </BrowserRouter>
        <Toaster position="top-right" />
      </LayoutProvider>
    </AuthProvider>
  )
}

export default App
