"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Slider } from "@/components/ui/slider"
import { Checkbox } from "@/components/ui/checkbox"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet"
import { MessageCircle, Heart, X, MapPin, Star, Send } from "lucide-react"

export default function HokieNest() {
  const [currentView, setCurrentView] = useState<"landing" | "onboarding" | "dashboard">("landing")
  const [selectedProperty, setSelectedProperty] = useState<any>(null)
  const [chatOpen, setChatOpen] = useState(false)
  const [preferences, setPreferences] = useState({
    cleanliness: [3],
    noiseLevel: [3],
    studyTime: [3],
    socialLevel: [3],
    sleepSchedule: [3],
  })

  // Mock data
  const roommates = [
    {
      id: 1,
      name: "Sarah Chen",
      major: "Computer Science",
      year: "Junior",
      photo: "/college-student-portrait.png",
      compatibility: 92,
      matchingPrefs: ["Clean", "Quiet", "Early Bird"],
    },
    {
      id: 2,
      name: "Mike Johnson",
      major: "Engineering",
      year: "Sophomore",
      photo: "/college-student-portrait.png",
      compatibility: 87,
      matchingPrefs: ["Social", "Study Groups", "Night Owl"],
    },
    {
      id: 3,
      name: "Emma Davis",
      major: "Business",
      year: "Senior",
      photo: "/college-student-portrait.png",
      compatibility: 84,
      matchingPrefs: ["Organized", "Moderate Social", "Balanced"],
    },
  ]

  const properties = [
    {
      id: 1,
      address: "123 College Ave",
      price: "$800/month",
      bedrooms: 2,
      bathrooms: 1,
      distance: "0.5 miles to campus",
      rating: 4.5,
      photo: "/college-apartment-exterior.jpg",
      nearby: [
        { place: "Drillfield", time: "5 min walk" },
        { place: "D2 Dining", time: "3 min walk" },
        { place: "Kroger", time: "10 min walk" },
      ],
    },
    {
      id: 2,
      address: "456 University Blvd",
      price: "$950/month",
      bedrooms: 3,
      bathrooms: 2,
      distance: "0.8 miles to campus",
      rating: 4.2,
      photo: "/college-apartment-exterior.jpg",
      nearby: [
        { place: "Squires Center", time: "8 min walk" },
        { place: "Turner Place", time: "5 min walk" },
        { place: "CVS Pharmacy", time: "12 min walk" },
      ],
    },
  ]

  if (currentView === "landing") {
    return (
      <div className="min-h-screen bg-background">
        {/* Navigation */}
        <nav className="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center">
                <h1 className="text-2xl font-bold text-primary">HokieNest</h1>
              </div>
              <Button variant="outline" onClick={() => setCurrentView("onboarding")}>
                Sign In
              </Button>
            </div>
          </div>
        </nav>

        {/* Hero Section */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-20 text-center">
            <h1 className="text-5xl font-bold text-balance mb-6">Find Your Perfect Roommate & Home at VT</h1>
            <p className="text-xl text-muted-foreground mb-12 max-w-2xl mx-auto text-pretty">
              Connect with compatible roommates and discover the best housing options near Virginia Tech campus.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" className="text-lg px-8 py-6" onClick={() => setCurrentView("onboarding")}>
                Find Roommates
              </Button>
              <Button
                size="lg"
                variant="outline"
                className="text-lg px-8 py-6 bg-transparent"
                onClick={() => setCurrentView("dashboard")}
              >
                Browse Housing
              </Button>
            </div>
          </div>
        </main>
      </div>
    )
  }

  if (currentView === "onboarding") {
    return (
      <div className="min-h-screen bg-background">
        <nav className="border-b border-border">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <h1 className="text-2xl font-bold text-primary">HokieNest</h1>
              <Button variant="ghost" onClick={() => setCurrentView("landing")}>
                Back
              </Button>
            </div>
          </div>
        </nav>

        <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold mb-4">Create Your Profile</h1>
            <p className="text-muted-foreground">Help us find your perfect roommate match</p>
          </div>

          <Card className="p-8">
            <div className="grid md:grid-cols-2 gap-12">
              {/* Basic Info */}
              <div className="space-y-6">
                <h2 className="text-2xl font-semibold">Basic Information</h2>

                <div className="space-y-4">
                  <div>
                    <Label htmlFor="name">Full Name</Label>
                    <Input id="name" placeholder="Enter your name" />
                  </div>

                  <div>
                    <Label htmlFor="year">Year</Label>
                    <Input id="year" placeholder="Freshman, Sophomore, etc." />
                  </div>

                  <div>
                    <Label htmlFor="major">Major</Label>
                    <Input id="major" placeholder="Your major" />
                  </div>

                  <div>
                    <Label htmlFor="budget">Budget (per month)</Label>
                    <Input id="budget" placeholder="$800" />
                  </div>

                  <div>
                    <Label htmlFor="moveIn">Move-in Date</Label>
                    <Input id="moveIn" type="date" />
                  </div>
                </div>
              </div>

              {/* Preferences */}
              <div className="space-y-6">
                <h2 className="text-2xl font-semibold">Quick Preferences</h2>

                <div className="space-y-6">
                  <div>
                    <Label>Cleanliness Level</Label>
                    <Slider
                      value={preferences.cleanliness}
                      onValueChange={(value) => setPreferences({ ...preferences, cleanliness: value })}
                      max={5}
                      min={1}
                      step={1}
                      className="mt-2"
                    />
                    <div className="flex justify-between text-sm text-muted-foreground mt-1">
                      <span>Relaxed</span>
                      <span>Very Clean</span>
                    </div>
                  </div>

                  <div>
                    <Label>Noise Level</Label>
                    <Slider
                      value={preferences.noiseLevel}
                      onValueChange={(value) => setPreferences({ ...preferences, noiseLevel: value })}
                      max={5}
                      min={1}
                      step={1}
                      className="mt-2"
                    />
                    <div className="flex justify-between text-sm text-muted-foreground mt-1">
                      <span>Quiet</span>
                      <span>Lively</span>
                    </div>
                  </div>

                  <div>
                    <Label>Study Time</Label>
                    <Slider
                      value={preferences.studyTime}
                      onValueChange={(value) => setPreferences({ ...preferences, studyTime: value })}
                      max={5}
                      min={1}
                      step={1}
                      className="mt-2"
                    />
                    <div className="flex justify-between text-sm text-muted-foreground mt-1">
                      <span>Light</span>
                      <span>Intensive</span>
                    </div>
                  </div>

                  <div>
                    <Label>Social Level</Label>
                    <Slider
                      value={preferences.socialLevel}
                      onValueChange={(value) => setPreferences({ ...preferences, socialLevel: value })}
                      max={5}
                      min={1}
                      step={1}
                      className="mt-2"
                    />
                    <div className="flex justify-between text-sm text-muted-foreground mt-1">
                      <span>Private</span>
                      <span>Very Social</span>
                    </div>
                  </div>

                  <div>
                    <Label>Sleep Schedule</Label>
                    <Slider
                      value={preferences.sleepSchedule}
                      onValueChange={(value) => setPreferences({ ...preferences, sleepSchedule: value })}
                      max={5}
                      min={1}
                      step={1}
                      className="mt-2"
                    />
                    <div className="flex justify-between text-sm text-muted-foreground mt-1">
                      <span>Early Bird</span>
                      <span>Night Owl</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Location Preferences */}
            <div className="mt-12">
              <h2 className="text-2xl font-semibold mb-6">What's important to you?</h2>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {["Campus", "Restaurants", "Grocery", "Gym", "Nightlife", "Study Spots"].map((location) => (
                  <div key={location} className="flex items-center space-x-2">
                    <Checkbox id={location} />
                    <Label htmlFor={location}>{location}</Label>
                  </div>
                ))}
              </div>
            </div>

            <div className="mt-12 text-center">
              <Button size="lg" className="px-12" onClick={() => setCurrentView("dashboard")}>
                Create Profile
              </Button>
            </div>
          </Card>
        </main>
      </div>
    )
  }

  // Dashboard View
  return (
    <div className="min-h-screen bg-background">
      <nav className="border-b border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <h1 className="text-2xl font-bold text-primary">HokieNest</h1>
            <div className="flex items-center gap-4">
              <Sheet open={chatOpen} onOpenChange={setChatOpen}>
                <SheetTrigger asChild>
                  <Button variant="outline" size="sm">
                    <MessageCircle className="h-4 w-4 mr-2" />
                    Messages
                  </Button>
                </SheetTrigger>
                <SheetContent>
                  <SheetHeader>
                    <SheetTitle>Messages</SheetTitle>
                  </SheetHeader>
                  <div className="mt-6 space-y-4">
                    <div className="p-4 border rounded-lg">
                      <div className="flex items-center gap-3 mb-2">
                        <img src="/abstract-profile.png" alt="Sarah" className="w-8 h-8 rounded-full" />
                        <span className="font-medium">Sarah Chen</span>
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        Hey! I saw we're a 92% match. Want to chat about housing options?
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <Input placeholder="Type a message..." className="flex-1" />
                      <Button size="sm">
                        <Send className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </SheetContent>
              </Sheet>
              <Button variant="ghost" onClick={() => setCurrentView("landing")}>
                Sign Out
              </Button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Tabs defaultValue="roommates" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="roommates">Find Roommates</TabsTrigger>
            <TabsTrigger value="housing">Browse Housing</TabsTrigger>
            <TabsTrigger value="matches">My Matches</TabsTrigger>
          </TabsList>

          <TabsContent value="roommates" className="mt-8">
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {roommates.map((roommate) => (
                <Card key={roommate.id} className="p-6">
                  <div className="text-center">
                    <img
                      src={roommate.photo || "/placeholder.svg"}
                      alt={roommate.name}
                      className="w-24 h-24 rounded-full mx-auto mb-4 object-cover"
                    />
                    <h3 className="text-xl font-semibold mb-1">{roommate.name}</h3>
                    <p className="text-muted-foreground mb-2">
                      {roommate.major} • {roommate.year}
                    </p>

                    <Badge variant="secondary" className="text-lg font-bold mb-4 bg-accent text-accent-foreground">
                      {roommate.compatibility}% Match
                    </Badge>

                    <div className="flex flex-wrap gap-2 justify-center mb-6">
                      {roommate.matchingPrefs.map((pref) => (
                        <Badge key={pref} variant="outline" className="text-xs">
                          {pref}
                        </Badge>
                      ))}
                    </div>

                    <div className="flex gap-2">
                      <Button className="flex-1">
                        <MessageCircle className="h-4 w-4 mr-2" />
                        Message
                      </Button>
                      <Button variant="outline" size="icon">
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="housing" className="mt-8">
            <div className="space-y-6">
              {properties.map((property) => (
                <Card key={property.id} className="p-6">
                  <div className="flex gap-6">
                    <img
                      src={property.photo || "/placeholder.svg"}
                      alt={property.address}
                      className="w-48 h-32 rounded-lg object-cover"
                    />
                    <div className="flex-1">
                      <div className="flex justify-between items-start mb-2">
                        <h3 className="text-xl font-semibold">{property.address}</h3>
                        <span className="text-2xl font-bold text-primary">{property.price}</span>
                      </div>

                      <p className="text-muted-foreground mb-2">
                        {property.bedrooms} bed • {property.bathrooms} bath
                      </p>

                      <div className="flex items-center gap-4 mb-4">
                        <div className="flex items-center gap-1">
                          <MapPin className="h-4 w-4 text-muted-foreground" />
                          <span className="text-sm">{property.distance}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                          <span className="text-sm">{property.rating}</span>
                        </div>
                      </div>

                      <Dialog>
                        <DialogTrigger asChild>
                          <Button onClick={() => setSelectedProperty(property)}>View Details</Button>
                        </DialogTrigger>
                        <DialogContent className="max-w-2xl">
                          <DialogHeader>
                            <DialogTitle>{property.address}</DialogTitle>
                          </DialogHeader>
                          <div className="space-y-6">
                            <img
                              src={property.photo || "/placeholder.svg"}
                              alt={property.address}
                              className="w-full h-64 rounded-lg object-cover"
                            />

                            <div className="grid grid-cols-2 gap-4">
                              <div>
                                <h4 className="font-semibold mb-2">Details</h4>
                                <p>Price: {property.price}</p>
                                <p>Bedrooms: {property.bedrooms}</p>
                                <p>Bathrooms: {property.bathrooms}</p>
                                <p>Distance: {property.distance}</p>
                              </div>

                              <div>
                                <h4 className="font-semibold mb-2">What's Nearby</h4>
                                {property.nearby.map((item, index) => (
                                  <p key={index} className="text-sm">
                                    {item.place} - {item.time}
                                  </p>
                                ))}
                              </div>
                            </div>

                            <div className="flex gap-4">
                              <Button className="flex-1">
                                <Heart className="h-4 w-4 mr-2" />
                                Save
                              </Button>
                              <Button variant="outline" className="flex-1 bg-transparent">
                                Share with Roommates
                              </Button>
                            </div>
                          </div>
                        </DialogContent>
                      </Dialog>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="matches" className="mt-8">
            <div className="space-y-8">
              <div>
                <h2 className="text-2xl font-semibold mb-4">Your Connections</h2>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {roommates.slice(0, 2).map((roommate) => (
                    <Card key={roommate.id} className="p-4">
                      <div className="flex items-center gap-3">
                        <img
                          src={roommate.photo || "/placeholder.svg"}
                          alt={roommate.name}
                          className="w-12 h-12 rounded-full object-cover"
                        />
                        <div>
                          <h3 className="font-semibold">{roommate.name}</h3>
                          <p className="text-sm text-muted-foreground">{roommate.major}</p>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              </div>

              <div>
                <h2 className="text-2xl font-semibold mb-4">Form a Group</h2>
                <Card className="p-6">
                  <p className="text-muted-foreground mb-4">
                    Drag profiles together to form a roommate group and find housing together.
                  </p>
                  <Button className="w-full" disabled>
                    Find Housing for Group
                  </Button>
                </Card>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}
