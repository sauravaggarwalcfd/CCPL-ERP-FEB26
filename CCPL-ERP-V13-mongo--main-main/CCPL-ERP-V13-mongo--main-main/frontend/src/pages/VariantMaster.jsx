/**
 * Variant Master - Main Page
 * Unified master for managing Colours, Sizes, and UOMs with tabs
 */

import { useState, useEffect } from 'react';
import { useLayout } from '../context/LayoutContext';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Palette, Ruler, Scale } from 'lucide-react';
import ColourMaster from '../components/variant-master/ColourMaster';
import SizeMaster from '../components/variant-master/SizeMaster';
import UOMMaster from '../components/variant-master/UOMMaster';

const VariantMaster = () => {
  const { setTitle } = useLayout();
  const [activeTab, setActiveTab] = useState('colours');

  useEffect(() => {
    setTitle('Variant Master');
  }, [setTitle]);

  return (
    <Tabs value={activeTab} onValueChange={setActiveTab} className="flex flex-col h-full">
      {/* Sticky Top Bar */}
      <div className="bg-white p-4 border-b sticky top-0 z-10">
        <TabsList className="grid w-full max-w-md grid-cols-3">
          <TabsTrigger value="colours" className="flex items-center gap-2">
            <Palette className="w-4 h-4" />
            <span>Colours</span>
          </TabsTrigger>
          <TabsTrigger value="sizes" className="flex items-center gap-2">
            <Ruler className="w-4 h-4" />
            <span>Sizes</span>
          </TabsTrigger>
          <TabsTrigger value="uoms" className="flex items-center gap-2">
            <Scale className="w-4 h-4" />
            <span>UOM</span>
          </TabsTrigger>
        </TabsList>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto p-6 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <TabsContent value="colours" className="mt-0">
            <ColourMaster />
          </TabsContent>

          <TabsContent value="sizes" className="mt-0">
            <SizeMaster />
          </TabsContent>

          <TabsContent value="uoms" className="mt-0">
            <UOMMaster />
          </TabsContent>
        </div>
      </div>
    </Tabs>
  );
};

export default VariantMaster;
