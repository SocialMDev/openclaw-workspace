import { Sidebar } from "@/components/Sidebar";
import { ActivityFeed } from "@/components/ActivityFeed";
import { CalendarView } from "@/components/CalendarView";
import { GlobalSearch } from "@/components/GlobalSearch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Activity, Calendar, Search, LayoutDashboard } from "lucide-react";

export default function Dashboard() {
  return (
    <div className="flex h-screen bg-background">
      <Sidebar />
      <main className="flex-1 overflow-auto p-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-foreground flex items-center gap-3">
            <LayoutDashboard className="h-8 w-8 text-primary" />
            Mission Control
          </h1>
          <p className="text-muted-foreground mt-1">
            Monitor and manage your OpenClaw agent activities
          </p>
        </div>

        <Tabs defaultValue="activity" className="space-y-4">
          <TabsList className="grid w-full grid-cols-3 lg:w-[400px]">
            <TabsTrigger value="activity" className="flex items-center gap-2">
              <Activity className="h-4 w-4" />
              Activity
            </TabsTrigger>
            <TabsTrigger value="calendar" className="flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              Calendar
            </TabsTrigger>
            <TabsTrigger value="search" className="flex items-center gap-2">
              <Search className="h-4 w-4" />
              Search
            </TabsTrigger>
          </TabsList>

          <TabsContent value="activity" className="space-y-4">
            <ActivityFeed />
          </TabsContent>

          <TabsContent value="calendar" className="space-y-4">
            <CalendarView />
          </TabsContent>

          <TabsContent value="search" className="space-y-4">
            <GlobalSearch />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
