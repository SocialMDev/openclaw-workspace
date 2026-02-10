"use client";

import { useState } from "react";
import { useQuery, useMutation } from "convex/react";
import { api } from "@/convex/_generated/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
  DialogClose,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  ChevronLeft,
  ChevronRight,
  Plus,
  Calendar as CalendarIcon,
  Clock,
  CheckCircle,
  XCircle,
  Trash2,
} from "lucide-react";
import { format, addDays, startOfWeek, isSameDay, parseISO } from "date-fns";
import { cn, formatTime } from "@/lib/utils";

const colorOptions = [
  { value: "blue", label: "Blue", class: "bg-blue-500" },
  { value: "green", label: "Green", class: "bg-green-500" },
  { value: "purple", label: "Purple", class: "bg-purple-500" },
  { value: "yellow", label: "Yellow", class: "bg-yellow-500" },
  { value: "red", label: "Red", class: "bg-red-500" },
  { value: "pink", label: "Pink", class: "bg-pink-500" },
];

export function CalendarView() {
  const [currentWeek, setCurrentWeek] = useState(new Date());
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [newTask, setNewTask] = useState({
    name: "",
    description: "",
    cronExpression: "",
    nextRun: "",
    color: "blue",
  });

  const tasks = useQuery(api.calendar.list, { enabledOnly: false }) ?? [];
  const createTask = useMutation(api.calendar.create);
  const updateTask = useMutation(api.calendar.update);
  const deleteTask = useMutation(api.calendar.remove);

  const weekStart = startOfWeek(currentWeek, { weekStartsOn: 1 });
  const weekDays = Array.from({ length: 7 }, (_, i) => addDays(weekStart, i));

  const navigateWeek = (direction: "prev" | "next") => {
    setCurrentWeek((prev) => addDays(prev, direction === "prev" ? -7 : 7));
  };

  const getTasksForDay = (day: Date) => {
    return tasks.filter((task) => {
      const taskDate = new Date(task.nextRun);
      return isSameDay(taskDate, day);
    });
  };

  const handleCreateTask = async () => {
    await createTask({
      name: newTask.name,
      description: newTask.description,
      cronExpression: newTask.cronExpression || "0 9 * * *",
      nextRun: new Date(newTask.nextRun).getTime(),
      enabled: true,
      color: newTask.color,
    });
    setIsDialogOpen(false);
    setNewTask({ name: "", description: "", cronExpression: "", nextRun: "", color: "blue" });
  };

  const toggleTask = async (id: string, currentEnabled: boolean) => {
    await updateTask({ id, enabled: !currentEnabled });
  };

  const handleDeleteTask = async (id: string) => {
    await deleteTask({ id });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card className="bg-slate-900/50 border-slate-800">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button
                variant="outline"
                size="icon"
                onClick={() => navigateWeek("prev")}
                className="border-slate-700 text-slate-300"
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <div>
                <h2 className="text-xl font-bold text-white">
                  {format(weekStart, "MMMM yyyy")}
                </h2>
                <p className="text-sm text-slate-400">
                  Week of {format(weekStart, "MMM d")}
                </p>
              </div>
              <Button
                variant="outline"
                size="icon"
                onClick={() => navigateWeek("next")}
                className="border-slate-700 text-slate-300"
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
              <DialogTrigger asChild>
                <Button className="bg-blue-600 hover:bg-blue-700">
                  <Plus className="h-4 w-4 mr-2" />
                  Add Task
                </Button>
              </DialogTrigger>
              <DialogContent className="bg-slate-900 border-slate-800 text-white">
                <DialogHeader>
                  <DialogTitle>Add Scheduled Task</DialogTitle>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div>
                    <label className="text-sm text-slate-400">Task Name</label>
                    <Input
                      value={newTask.name}
                      onChange={(e) => setNewTask({ ...newTask, name: e.target.value })}
                      placeholder="Daily backup"
                      className="bg-slate-800 border-slate-700"
                    />
                  </div>
                  <div>
                    <label className="text-sm text-slate-400">Description</label>
                    <Input
                      value={newTask.description}
                      onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
                      placeholder="Backup all data to cloud storage"
                      className="bg-slate-800 border-slate-700"
                    />
                  </div>
                  <div>
                    <label className="text-sm text-slate-400">Cron Expression</label>
                    <Input
                      value={newTask.cronExpression}
                      onChange={(e) => setNewTask({ ...newTask, cronExpression: e.target.value })}
                      placeholder="0 9 * * *"
                      className="bg-slate-800 border-slate-700"
                    />
                    <p className="text-xs text-slate-500 mt-1">
                      Format: minute hour day month weekday
                    </p>
                  </div>
                  <div>
                    <label className="text-sm text-slate-400">Next Run</label>
                    <Input
                      type="datetime-local"
                      value={newTask.nextRun}
                      onChange={(e) => setNewTask({ ...newTask, nextRun: e.target.value })}
                      className="bg-slate-800 border-slate-700"
                    />
                  </div>
                  <div>
                    <label className="text-sm text-slate-400">Color</label>
                    <Select
                      value={newTask.color}
                      onValueChange={(value) => setNewTask({ ...newTask, color: value })}
                    >
                      <SelectTrigger className="bg-slate-800 border-slate-700">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="bg-slate-800 border-slate-700">
                        {colorOptions.map((color) => (
                          <SelectItem key={color.value} value={color.value}>
                            <div className="flex items-center gap-2">
                              <div className={cn("w-4 h-4 rounded-full", color.class)} />
                              {color.label}
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <DialogFooter>
                  <DialogClose asChild>
                    <Button variant="outline" className="border-slate-700">Cancel</Button>
                  </DialogClose>
                  <Button onClick={handleCreateTask} className="bg-blue-600 hover:bg-blue-700">
                    Create Task
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        </CardContent>
      </Card>

      {/* Calendar Grid */}
      <div className="grid grid-cols-7 gap-4">
        {weekDays.map((day, index) => {
          const dayTasks = getTasksForDay(day);
          const isToday = isSameDay(day, new Date());
          
          return (
            <Card
              key={index}
              className={cn(
                "bg-slate-900/50 border-slate-800 min-h-[300px]",
                isToday && "border-blue-500/50 ring-1 ring-blue-500/20"
              )}
            >
              <CardHeader className="p-3">
                <div className="text-center">
                  <p className="text-xs text-slate-500 uppercase">{format(day, "EEE")}</p>
                  <p
                    className={cn(
                      "text-lg font-bold",
                      isToday ? "text-blue-400" : "text-white"
                    )}
                  >
                    {format(day, "d")}
                  </p>
                </div>
              </CardHeader>
              <CardContent className="p-3 pt-0 space-y-2">
                {dayTasks.map((task) => (
                  <div
                    key={task._id}
                    className={cn(
                      "p-2 rounded-lg border text-xs group relative",
                      task.enabled
                        ? "bg-slate-800/50 border-slate-700"
                        : "bg-slate-800/20 border-slate-800 opacity-50"
                    )}
                  >
                    <div className="flex items-center gap-2">
                      <div
                        className={cn(
                          "w-2 h-2 rounded-full",
                          colorOptions.find((c) => c.value === task.color)?.class || "bg-blue-500"
                        )}
                      />
                      <span className="font-medium text-white truncate">{task.name}</span>
                    </div>
                    <p className="text-slate-400 mt-1 truncate">{task.description}</p>
                    <div className="flex items-center gap-1 mt-1 text-slate-500">
                      <Clock className="h-3 w-3" />
                      <span>{formatTime(task.nextRun)}</span>
                    </div>
                    <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
                      <button
                        onClick={() => toggleTask(task._id, task.enabled)}
                        className="p-1 rounded hover:bg-slate-700"
                      >
                        {task.enabled ? (
                          <CheckCircle className="h-3 w-3 text-green-500" />
                        ) : (
                          <XCircle className="h-3 w-3 text-red-500" />
                        )}
                      </button>
                      <button
                        onClick={() => handleDeleteTask(task._id)}
                        className="p-1 rounded hover:bg-slate-700"
                      >
                        <Trash2 className="h-3 w-3 text-red-400" />
                      </button>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Upcoming Tasks */}
      <Card className="bg-slate-900/50 border-slate-800">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <CalendarIcon className="h-5 w-5" />
            Upcoming Tasks
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {tasks
              .filter((t) => t.enabled)
              .sort((a, b) => a.nextRun - b.nextRun)
              .slice(0, 5)
              .map((task) => (
                <div
                  key={task._id}
                  className="flex items-center justify-between p-3 rounded-lg bg-slate-800/30 border border-slate-700/50"
                >
                  <div className="flex items-center gap-3">
                    <div
                      className={cn(
                        "w-3 h-3 rounded-full",
                        colorOptions.find((c) => c.value === task.color)?.class || "bg-blue-500"
                      )}
                    />
                    <div>
                      <p className="text-sm font-medium text-white">{task.name}</p>
                      <p className="text-xs text-slate-400">{task.description}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-slate-300">
                      {format(new Date(task.nextRun), "MMM d, yyyy")}
                    </p>
                    <p className="text-xs text-slate-500">{formatTime(task.nextRun)}</p>
                  </div>
                </div>
              ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
