from datetime import datetime

from django.core.paginator import Paginator
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from uuid import UUID

from ...models import FilmWork

class FilmWorkListApi(APIView):
    def get(self, request):
        """
        Handles the GET request for listing movies with pagination.
        """
        try:
            page_string: str = request.query_params.get('page', '1')
            page = 1
            if page_string.isnumeric():
                page = int(page_string)
                if page < 1:
                    page = 1
        except ValueError:
            return Response({'error': 'Invalid page number. Must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)

        paginator = Paginator(FilmWork.objects.all(), per_page=50)  # Adjust per_page as needed
        movies = paginator.page(page)

        results = []
        for movie in movies.object_list:
            results.append(form_movie_data(movie))
        if page_string == 'last' or page > paginator.num_pages:
            page = paginator.num_pages
        data = {
            'count': FilmWork.objects.count(),
            'total_pages': paginator.num_pages,
            'prev': page - 1 if paginator.get_page(page).has_previous() else None,
            'next': page + 1 if paginator.get_page(page).has_next() else None,
            'results': results,
        }

        return Response(data)


def form_movie_data(movie: FilmWork) -> dict[str, str]:
    """
    Forms a dict representation of the FilmWork instance
    """
    data = {
        'id': str(movie.id),
        'title': movie.title,
        'description': movie.description,
        'creation_date': movie.creation_date.isoformat() if movie.creation_date else datetime.now().date().isoformat(),
        'rating': movie.rating or 0.0,
        'type': movie.type,
        'genres': [str(genre) for genre in movie.genres.all()],
        'actors': [str(person) for person in movie.persons.filter(
            personfilmwork__role='actor').all()],
        'directors': [str(person) for person in movie.persons.filter(
            personfilmwork__role='director').all()],
        'writers': [str(person) for person in movie.persons.filter(
            personfilmwork__role='writer').all()],
    }
    return data


class FilmWorkDetailApi(APIView):
    def get(self, request, pk: str):
        """
        Handles the GET request for a specific movie by ID.
        """
        try:
            movie_id = UUID(pk)
        except ValueError:
            return Response({'error': 'Invalid UUID format'}, status=status.HTTP_404_NOT_FOUND)

        try:
            movie = FilmWork.objects.get(id=movie_id)
        except FilmWork.DoesNotExist:
            return Response({'error': 'FilmWork not found'}, status=status.HTTP_404_NOT_FOUND)

        data = form_movie_data(movie)

        return Response(data)
