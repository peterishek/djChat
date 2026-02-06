# Import necessary modules and classes from Django and DRF
from django.shortcuts import render
from rest_framework import viewsets
from django.db.models import Count
from .serializers import ServerSerializer
from rest_framework.response import Response
from .models import Server
from .schema import server_list_docs
from rest_framework.exceptions import AuthenticationFailed, ValidationError

# ViewSet to list Server objects with filtering options like category, user, server ID, and member count

class ServerListViewSet(viewsets.ViewSet):

    # Base queryset containing all Server records
    queryset = Server.objects.all()

    # Handles GET requests to list servers
    @server_list_docs
    def list(self, request):

        
        """
        Retrieves a filtered list of server objects based on query parameters.

        This method processes various query parameters to filter, limit, and 
        annotate a queryset of server objects. It allows filtering by category 
        name, user membership, or a specific server ID. Optionally, it can 
        annotate each server with its member count and limit the number of 
        servers returned. The method also includes authentication checks where 
        necessary.

        Args:
            request (Request): The HTTP request object containing user information
                and optional query parameters. The method supports the following 
                query parameters:

                - category (str, optional): Filters servers to only include those 
                belonging to the specified category name.

                - qty (int, optional): If specified, limits the number of servers 
                returned to the given integer quantity.

                - by_user (str, optional): If set to "true", filters servers to 
                include only those in which the authenticated user is a member. 
                Authentication is required.

                - by_serverid (str, optional): Filters the servers to include only 
                the one with the specified server ID. Authentication is required.

                - with_num_members (str, optional): If set to "true", annotates 
                each returned server with the number of members (`num_members`).

        Raises:
            AuthenticationFailed: If either `by_user=true` or `by_serverid` is used 
                and the user is not authenticated.

            ValidationError:
                - If `by_serverid` is provided and no server with the given ID exists.
                - If the server ID provided is not a valid integer.

        Returns:
            QuerySet: A Django QuerySet containing filtered `Server` objects. The 
            queryset may be:
                - Filtered by category, server ID, or user membership
                - Annotated with `num_members` if requested
                - Limited to a specific number of results via `qty`

        Notes:
            - The method assumes a custom middleware attaches a `user_id` attribute 
            to the request object.
            - `qty` must be an integer-like string; otherwise, a `ValueError` will be raised.
            - If `by_serverid` is provided, the method ensures that the server exists; 
            otherwise, it raises a `ValidationError`.

        Example:
            GET /api/servers/?category=education&qty=10&with_num_members=true&by_user=true

            Returns up to 10 servers in the "education" category that the current 
            user is a member of, each annotated with the number of members.
        """

        # Extract optional query parameters from the request URL
        category = request.query_params.get("category")                   # Filter by category name
        qty = request.query_params.get("qty")                             # Limit number of servers returned
        by_user = request.query_params.get("by_user") == "true"           # Check if filtering by user membership
        by_serverid = request.query_params.get("by_serverid")             # Specific server ID to retrieve
        with_num_members = request.query_params.get("with_num_members") == "true"  # Whether to include member count
    

        # Authentication required if filtering by user or server ID
        if (by_user or by_serverid) and not request.user.is_authenticated:
            raise AuthenticationFailed()

        # Filter servers by category name, if provided
        if category:
            self.queryset = self.queryset.filter(category__name=category)

        # Filter servers where the current user is a member
        if by_user:
            user_id = request.user_id  # Assumes custom middleware adds `user_id` attribute to request
            self.queryset = self.queryset.filter(members=user_id)

        # Annotate the queryset with number of members, if requested
        if with_num_members:
            self.queryset = self.queryset.annotate(num_members=Count("members"))

        # Limit the number of servers returned, if `qty` is specified
        if qty:
            self.queryset = self.queryset[: int(qty)]  

        # If a specific server ID is given, filter the queryset and validate the result
        if by_serverid:
            try:
                self.queryset = self.queryset.filter(id=by_serverid)
                # Raise error if no matching server found
                if not self.queryset.exists():
                    raise ValidationError(detail=f"Server with id {by_serverid} not found")
            except ValueError:
                # handle invalid server id format (e.g., non-integer)
                raise ValidationError(detail="invalid")

        # Serialize the filtered queryset; pass context to control conditional fields like `num_members`
        serializer = ServerSerializer(self.queryset, many=True, context={"num_members": with_num_members})

        # Return the serialized server data as a JSON response
        return Response(serializer.data)
