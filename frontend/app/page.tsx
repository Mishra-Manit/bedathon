"use client"

import { useEffect, useState } from "react"
import { supabase } from "@/lib/supabaseClient"
import type { User } from "@supabase/supabase-js"
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
import { MessageCircle, Heart, X, MapPin, Star, Send, Moon, Sun, Loader2, Phone, CheckCircle, XCircle, AlertCircle, Home } from "lucide-react"
import { useApartments } from "@/lib/useApartments"
import { formatApartmentForDisplay } from "@/lib/apartmentService"

export default function HokieNest() {
  const [currentView, setCurrentView] = useState<"landing" | "onboarding" | "dashboard">("landing")
  const [user, setUser] = useState<User | null>(null)
  const [selectedProperty, setSelectedProperty] = useState<any>(null)
  const [chatOpen, setChatOpen] = useState(false)
  const [darkMode, setDarkMode] = useState(false)
  
  // Fetch apartment data
  const { apartments, loading: apartmentsLoading, error: apartmentsError } = useApartments()
  const [preferences, setPreferences] = useState({
    cleanliness: [3],
    noiseLevel: [3],
    studyTime: [3],
    socialLevel: [3],
    sleepSchedule: [3],
  })

  useEffect(() => {
    let isMounted = true
    ;(async () => {
      const { data } = await supabase.auth.getSession()
      if (isMounted) {
        setUser(data.session?.user ?? null)
        if (data.session?.user) {
          setCurrentView("dashboard")
        }
      }
    })()
    const { data: authListener } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null)
      if (session?.user) {
        setCurrentView("dashboard")
      } else {
        setCurrentView("landing")
      }
    })
    return () => {
      authListener.subscription.unsubscribe()
      isMounted = false
    }
  }, [])

  const signInWithGoogle = async () => {
    await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: typeof window !== "undefined" ? window.location.origin : undefined,
      },
    })
  }

  const signOut = async () => {
    await supabase.auth.signOut()
    setCurrentView("landing")
  }

  const toggleDarkMode = () => {
    setDarkMode(!darkMode)
    document.documentElement.classList.toggle("dark")
  }

  // Mock data
  const roommates = [
    {
      id: 1,
      name: "Sarah Chen",
      major: "Computer Science",
      year: "Junior",
      photo: "/person-placeholder-1.png",
      compatibility: 92,
      matchingPrefs: ["Clean", "Quiet", "Early Bird"],
    },
    {
      id: 2,
      name: "Mike Johnson",
      major: "Engineering",
      year: "Sophomore",
      photo: "/person-placeholder-2.png",
      compatibility: 87,
      matchingPrefs: ["Social", "Study Groups", "Night Owl"],
    },
    {
      id: 3,
      name: "Emma Davis",
      major: "Business",
      year: "Senior",
      photo: "/person-placeholder-3.png",
      compatibility: 84,
      matchingPrefs: ["Organized", "Moderate Social", "Balanced"],
    },
  ]

  // Format apartments for display
  const properties = apartments.map(apartment => formatApartmentForDisplay(apartment))

  if (currentView === "landing") {
    return (
      <div className="min-h-screen bg-background">
        <nav className="sticky top-0 z-50 border-b border-border bg-background/80 backdrop-blur-md supports-[backdrop-filter]:bg-background/60">
          <div className="max-w-6xl mx-auto px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center">
                <h1 className="text-2xl font-bold tracking-tight">HokieNest</h1>
              </div>
              <div className="flex items-center gap-4">
                <Button variant="ghost" size="sm" onClick={toggleDarkMode} className="w-9 h-9 p-0">
                  {darkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
                </Button>
                {user ? (
                  <Button variant="outline" onClick={() => setCurrentView("dashboard")}>Dashboard</Button>
                ) : (
                  <Button variant="outline" onClick={signInWithGoogle}>Sign in with Google</Button>
                )}
              </div>
            </div>
          </div>
        </nav>

        <main className="max-w-6xl mx-auto px-6 lg:px-8">
          <div className="py-32 text-center">
            <h1 className="text-6xl font-bold tracking-tight text-balance mb-8 leading-tight">
              Find Your Perfect
              <br />
              <span className="text-primary">Roommate & Home</span>
              <br />
              at Virginia Tech
            </h1>
            <p className="text-xl text-muted-foreground mb-16 max-w-2xl mx-auto text-pretty leading-relaxed">
              Connect with compatible roommates and discover the best housing options near campus with our intelligent
              matching system.
            </p>

            <div className="flex flex-col sm:flex-row gap-6 justify-center">
              <Button
                size="lg"
                className="text-lg px-10 py-6 h-auto font-medium shadow-lg hover:shadow-xl transition-all duration-150"
                onClick={() => (user ? setCurrentView("dashboard") : signInWithGoogle())}
              >
                {user ? "Go to Dashboard" : "Find Roommates"}
              </Button>
              <Button
                size="lg"
                variant="outline"
                className="text-lg px-10 py-6 h-auto font-medium bg-transparent"
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
        <nav className="sticky top-0 z-50 border-b border-border bg-background/80 backdrop-blur-md">
          <div className="max-w-6xl mx-auto px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <h1 className="text-2xl font-bold tracking-tight">HokieNest</h1>
              <div className="flex items-center gap-4">
                <Button variant="ghost" size="sm" onClick={toggleDarkMode} className="w-9 h-9 p-0">
                  {darkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
                </Button>
                <Button variant="ghost" onClick={() => setCurrentView("landing")}>
                  Back
                </Button>
              </div>
            </div>
          </div>
        </nav>

        <main className="max-w-5xl mx-auto px-6 lg:px-8 py-16">
          <div className="text-center mb-16">
            <h1 className="text-5xl font-bold mb-6 tracking-tight">Create Your Profile</h1>
            <p className="text-xl text-muted-foreground">Help us find your perfect roommate match</p>
          </div>

          <Card className="p-12 card-hover border-border/50">
            <div className="grid md:grid-cols-2 gap-16">
              {/* Basic Info */}
              <div className="space-y-8">
                <h2 className="text-3xl font-bold tracking-tight">Basic Information</h2>

                <div className="space-y-6">
                  <div className="space-y-3">
                    <Label htmlFor="name" className="text-sm font-medium text-foreground">
                      Full Name
                    </Label>
                    <Input
                      id="name"
                      placeholder="Enter your name"
                      className="h-12 border-border/50 bg-input/50 focus:bg-background transition-colors"
                    />
                  </div>

                  <div className="space-y-3">
                    <Label htmlFor="year" className="text-sm font-medium text-foreground">
                      Year
                    </Label>
                    <Input
                      id="year"
                      placeholder="Freshman, Sophomore, etc."
                      className="h-12 border-border/50 bg-input/50 focus:bg-background transition-colors"
                    />
                  </div>

                  <div className="space-y-3">
                    <Label htmlFor="major" className="text-sm font-medium text-foreground">
                      Major
                    </Label>
                    <Input
                      id="major"
                      placeholder="Your major"
                      className="h-12 border-border/50 bg-input/50 focus:bg-background transition-colors"
                    />
                  </div>

                  <div className="space-y-3">
                    <Label htmlFor="budget" className="text-sm font-medium text-foreground">
                      Budget (per month)
                    </Label>
                    <Input
                      id="budget"
                      placeholder="$800"
                      className="h-12 border-border/50 bg-input/50 focus:bg-background transition-colors"
                    />
                  </div>

                  <div className="space-y-3">
                    <Label htmlFor="moveIn" className="text-sm font-medium text-foreground">
                      Move-in Date
                    </Label>
                    <Input
                      id="moveIn"
                      type="date"
                      className="h-12 border-border/50 bg-input/50 focus:bg-background transition-colors"
                    />
                  </div>
                </div>
              </div>

              {/* Preferences */}
              <div className="space-y-8">
                <h2 className="text-3xl font-bold tracking-tight">Quick Preferences</h2>

                <div className="space-y-8">
                  <div className="space-y-4">
                    <Label className="text-sm font-medium text-foreground">Cleanliness Level</Label>
                    <Slider
                      value={preferences.cleanliness}
                      onValueChange={(value) => setPreferences({ ...preferences, cleanliness: value })}
                      max={5}
                      min={1}
                      step={1}
                      className="mt-3"
                    />
                    <div className="flex justify-between text-sm text-muted-foreground mt-2">
                      <span>Relaxed</span>
                      <span>Very Clean</span>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <Label className="text-sm font-medium text-foreground">Noise Level</Label>
                    <Slider
                      value={preferences.noiseLevel}
                      onValueChange={(value) => setPreferences({ ...preferences, noiseLevel: value })}
                      max={5}
                      min={1}
                      step={1}
                      className="mt-3"
                    />
                    <div className="flex justify-between text-sm text-muted-foreground mt-2">
                      <span>Quiet</span>
                      <span>Lively</span>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <Label className="text-sm font-medium text-foreground">Study Time</Label>
                    <Slider
                      value={preferences.studyTime}
                      onValueChange={(value) => setPreferences({ ...preferences, studyTime: value })}
                      max={5}
                      min={1}
                      step={1}
                      className="mt-3"
                    />
                    <div className="flex justify-between text-sm text-muted-foreground mt-2">
                      <span>Light</span>
                      <span>Intensive</span>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <Label className="text-sm font-medium text-foreground">Social Level</Label>
                    <Slider
                      value={preferences.socialLevel}
                      onValueChange={(value) => setPreferences({ ...preferences, socialLevel: value })}
                      max={5}
                      min={1}
                      step={1}
                      className="mt-3"
                    />
                    <div className="flex justify-between text-sm text-muted-foreground mt-2">
                      <span>Private</span>
                      <span>Very Social</span>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <Label className="text-sm font-medium text-foreground">Sleep Schedule</Label>
                    <Slider
                      value={preferences.sleepSchedule}
                      onValueChange={(value) => setPreferences({ ...preferences, sleepSchedule: value })}
                      max={5}
                      min={1}
                      step={1}
                      className="mt-3"
                    />
                    <div className="flex justify-between text-sm text-muted-foreground mt-2">
                      <span>Early Bird</span>
                      <span>Night Owl</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Location Preferences */}
            <div className="mt-16 pt-12 border-t border-border/50">
              <h2 className="text-3xl font-bold mb-8 tracking-tight">What's important to you?</h2>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
                {["Campus", "Restaurants", "Grocery", "Gym", "Nightlife", "Study Spots"].map((location) => (
                  <div key={location} className="flex items-center space-x-3">
                    <Checkbox id={location} />
                    <Label htmlFor={location} className="text-sm font-medium">
                      {location}
                    </Label>
                  </div>
                ))}
              </div>
            </div>

            <div className="mt-16 text-center">
              <Button
                size="lg"
                className="px-16 py-6 h-auto text-lg font-medium shadow-lg hover:shadow-xl transition-all duration-150"
                onClick={() => setCurrentView("dashboard")}
              >
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
      <nav className="sticky top-0 z-50 border-b border-border bg-background/80 backdrop-blur-md">
        <div className="max-w-6xl mx-auto px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <h1 className="text-2xl font-bold tracking-tight">HokieNest</h1>
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="sm" onClick={toggleDarkMode} className="w-9 h-9 p-0">
                {darkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
              </Button>
              <Sheet open={chatOpen} onOpenChange={setChatOpen}>
                <SheetTrigger asChild>
                  <Button variant="outline" size="sm" className="gap-2 bg-transparent">
                    <MessageCircle className="h-4 w-4" />
                    Messages
                  </Button>
                </SheetTrigger>
                <SheetContent className="backdrop-blur-md bg-background/95">
                  <SheetHeader>
                    <SheetTitle className="text-xl font-bold">Messages</SheetTitle>
                  </SheetHeader>
                  <div className="mt-8 space-y-6">
                    <div className="p-6 border border-border/50 rounded-lg card-hover">
                      <div className="flex items-center gap-3 mb-3">
                        <img src="/abstract-profile.png" alt="Sarah" className="w-10 h-10 rounded-full" />
                        <span className="font-medium">Sarah Chen</span>
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      </div>
                      <p className="text-sm text-muted-foreground leading-relaxed">
                        Hey! I saw we're a 92% match. Want to chat about housing options?
                      </p>
                    </div>
                    <div className="flex gap-3">
                      <Input
                        placeholder="Type a message..."
                        className="flex-1 h-12 border-border/50 bg-input/50 focus:bg-background transition-colors"
                      />
                      <Button size="sm" className="h-12 px-4">
                        <Send className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </SheetContent>
              </Sheet>
              {user ? (
                <Button variant="ghost" onClick={signOut}>Sign Out</Button>
              ) : (
                <Button variant="ghost" onClick={signInWithGoogle}>Sign In</Button>
              )}
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto px-6 lg:px-8 py-12">
        <Tabs defaultValue="roommates" className="w-full">
          <TabsList className="grid w-full grid-cols-3 h-12 p-1 bg-muted/50">
            <TabsTrigger value="roommates" className="font-medium">
              Find Roommates
            </TabsTrigger>
            <TabsTrigger value="housing" className="font-medium">
              Browse Housing
            </TabsTrigger>
            <TabsTrigger value="matches" className="font-medium">
              My Matches
            </TabsTrigger>
          </TabsList>

          <TabsContent value="roommates" className="mt-12">
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
              {roommates.map((roommate) => (
                <Card key={roommate.id} className="p-8 card-hover border-border/50">
                  <div className="text-center">
                    <img
                      src={roommate.photo || "/placeholder.svg"}
                      alt={roommate.name}
                      className="w-28 h-28 rounded-full mx-auto mb-6 object-cover border-2 border-border/20"
                    />
                    <h3 className="text-xl font-bold mb-2 tracking-tight">{roommate.name}</h3>
                    <p className="text-muted-foreground mb-4 text-sm">
                      {roommate.major} • {roommate.year}
                    </p>

                    <Badge
                      variant="secondary"
                      className="text-lg font-bold mb-6 bg-primary/10 text-primary border-primary/20 px-4 py-2"
                    >
                      {roommate.compatibility}% Match
                    </Badge>

                    <div className="flex flex-wrap gap-2 justify-center mb-8">
                      {roommate.matchingPrefs.map((pref) => (
                        <Badge key={pref} variant="outline" className="text-xs border-border/50">
                          {pref}
                        </Badge>
                      ))}
                    </div>

                    <div className="flex gap-3">
                      <Button className="flex-1 gap-2 h-11 font-medium">
                        <MessageCircle className="h-4 w-4" />
                        Message
                      </Button>
                      <Button variant="outline" size="icon" className="h-11 w-11 bg-transparent">
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="housing" className="mt-12">
            <div className="space-y-8">
              {apartmentsLoading ? (
                <div className="flex items-center justify-center py-12">
                  <Loader2 className="h-8 w-8 animate-spin" />
                  <span className="ml-2">Loading apartments...</span>
                </div>
              ) : apartmentsError ? (
                <div className="text-center py-12">
                  <AlertCircle className="h-12 w-12 mx-auto text-red-500 mb-4" />
                  <p className="text-red-500">Error loading apartments: {apartmentsError}</p>
                </div>
              ) : properties.length === 0 ? (
                <div className="text-center py-12">
                  <Home className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">No apartments found</p>
                </div>
              ) : (
                properties.map((property) => (
                <Card key={property.id} className="p-8 card-hover border-border/50">
                  <div className="flex gap-8">
                    <img
                      src={property.imageUrl || "/college-apartment-exterior.jpg"}
                      alt={property.name}
                      className="w-56 h-40 rounded-lg object-cover border border-border/20"
                    />
                    <div className="flex-1">
                      <div className="flex justify-between items-start mb-4">
                        <h3 className="text-2xl font-bold tracking-tight">{property.name}</h3>
                        <span className="text-3xl font-bold text-primary">{property.price}</span>
                      </div>

                      <p className="text-muted-foreground mb-4 text-lg">
                        {property.bedrooms} • {property.address}
                      </p>

                      <div className="flex items-center gap-6 mb-6">
                        <div className="flex items-center gap-2">
                          <MapPin className="h-4 w-4 text-muted-foreground" />
                          <span className="text-sm">{property.distance}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          {property.busStop ? (
                            <CheckCircle className="h-4 w-4 text-green-500" />
                          ) : (
                            <XCircle className="h-4 w-4 text-red-500" />
                          )}
                          <span className="text-sm font-medium">{property.busStop || 'No bus stop'}</span>
                        </div>
                      </div>

                      <Dialog>
                        <DialogTrigger asChild>
                          <Button
                            onClick={() => setSelectedProperty(property)}
                            className="h-11 px-8 font-medium shadow-md hover:shadow-lg transition-all duration-150"
                          >
                            View Details
                          </Button>
                        </DialogTrigger>
                        <DialogContent className="max-w-3xl backdrop-blur-md bg-background/95">
                          <DialogHeader>
                            <DialogTitle className="text-2xl font-bold">{property.name}</DialogTitle>
                          </DialogHeader>
                          <div className="space-y-8">
                            <img
                              src={property.imageUrl || "/college-apartment-exterior.jpg"}
                              alt={property.name}
                              className="w-full h-80 rounded-lg object-cover border border-border/20"
                            />

                            <div className="grid grid-cols-2 gap-8">
                              <div>
                                <h4 className="font-bold mb-4 text-lg">Details</h4>
                                <div className="space-y-2 text-sm">
                                  <p>
                                    <span className="font-medium">Price:</span> {property.price}
                                  </p>
                                  <p>
                                    <span className="font-medium">Bedrooms:</span> {property.bedrooms}
                                  </p>
                                  <p>
                                    <span className="font-medium">Address:</span> {property.address}
                                  </p>
                                  <p>
                                    <span className="font-medium">Distance:</span> {property.distance}
                                  </p>
                                  <p>
                                    <span className="font-medium">Lease Type:</span> {property.leaseType}
                                  </p>
                                  <p>
                                    <span className="font-medium">Lease Term:</span> {property.leaseTerm}
                                  </p>
                                </div>
                              </div>

                              <div>
                                <h4 className="font-bold mb-4 text-lg">Amenities & Features</h4>
                                <div className="space-y-2">
                                  <p className="text-sm">
                                    <span className="font-medium">Pets:</span> {property.pets}
                                  </p>
                                  <p className="text-sm">
                                    <span className="font-medium">Parking:</span> {property.parking}
                                  </p>
                                  <p className="text-sm">
                                    <span className="font-medium">Furniture:</span> {property.furniture}
                                  </p>
                                  <p className="text-sm">
                                    <span className="font-medium">Laundry:</span> {property.laundry}
                                  </p>
                                  <p className="text-sm">
                                    <span className="font-medium">Utilities:</span> {property.utilities}
                                  </p>
                                  <p className="text-sm">
                                    <span className="font-medium">Bus Stop:</span> {property.busStop}
                                  </p>
                                </div>
                              </div>
                            </div>

                            <div className="grid grid-cols-2 gap-8">
                              <div>
                                <h4 className="font-bold mb-4 text-lg">Contact & Fees</h4>
                                <div className="space-y-2 text-sm">
                                  <p>
                                    <span className="font-medium">Phone:</span> {property.phone}
                                  </p>
                                  <p>
                                    <span className="font-medium">Application Fee:</span> {property.applicationFee}
                                  </p>
                                  <p>
                                    <span className="font-medium">Security Deposit:</span> {property.securityDeposit}
                                  </p>
                                  <p>
                                    <span className="font-medium">Additional Fees:</span> {property.additionalFees}
                                  </p>
                                </div>
                              </div>

                              <div>
                                <h4 className="font-bold mb-4 text-lg">Notes</h4>
                                <div className="space-y-2">
                                  <p className="text-sm text-muted-foreground">
                                    {property.notes || 'No additional notes available'}
                                  </p>
                                </div>
                              </div>
                            </div>

                            <div className="flex gap-4">
                              <Button className="flex-1 gap-2 h-12 font-medium shadow-md hover:shadow-lg transition-all duration-150">
                                <Heart className="h-4 w-4" />
                                Save
                              </Button>
                              <Button variant="outline" className="flex-1 h-12 font-medium bg-transparent">
                                Share with Roommates
                              </Button>
                            </div>
                          </div>
                        </DialogContent>
                      </Dialog>
                    </div>
                  </div>
                </Card>
                ))
              )}
            </div>
          </TabsContent>

          <TabsContent value="matches" className="mt-12">
            <div className="space-y-12">
              <div>
                <h2 className="text-3xl font-bold mb-8 tracking-tight">Your Connections</h2>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {roommates.slice(0, 2).map((roommate) => (
                    <Card key={roommate.id} className="p-6 card-hover border-border/50">
                      <div className="flex items-center gap-4">
                        <img
                          src={roommate.photo || "/placeholder.svg"}
                          alt={roommate.name}
                          className="w-16 h-16 rounded-full object-cover border-2 border-border/20"
                        />
                        <div>
                          <h3 className="font-bold text-lg">{roommate.name}</h3>
                          <p className="text-sm text-muted-foreground">{roommate.major}</p>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              </div>

              <div>
                <h2 className="text-3xl font-bold mb-8 tracking-tight">Form a Group</h2>
                <Card className="p-8 card-hover border-border/50">
                  <p className="text-muted-foreground mb-6 text-lg leading-relaxed">
                    Drag profiles together to form a roommate group and find housing together.
                  </p>
                  <Button className="w-full h-12 font-medium" disabled>
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
