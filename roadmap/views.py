from django.shortcuts import render, redirect, get_object_or_404

from .forms import StudentProfileForm
from .models import Roadmap, RoadmapStep
from .services.ollama_service import generate_roadmap


def home(request):
    if request.method == "POST":
        form = StudentProfileForm(request.POST)
        if form.is_valid():
            profile = form.save()

            steps, source, raw_response = generate_roadmap(profile)

            roadmap = Roadmap.objects.create(
                profile=profile, source=source, raw_llm_response=raw_response
            )
            RoadmapStep.objects.bulk_create(
                [
                    RoadmapStep(
                        roadmap=roadmap,
                        order=i,
                        title=step["title"],
                        description=step.get("description", ""),
                    )
                    for i, step in enumerate(steps, start=1)
                ]
            )
            return redirect("roadmap_result", pk=roadmap.pk)
    else:
        form = StudentProfileForm()

    return render(request, "roadmap/home.html", {"form": form})


def result(request, pk):
    roadmap = get_object_or_404(Roadmap, pk=pk)
    return render(
        request,
        "roadmap/result.html",
        {"roadmap": roadmap, "profile": roadmap.profile, "steps": roadmap.steps.all()},
    )
