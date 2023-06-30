
% Initialize graph and its elements
Nodes = load('Nodes2.txt');
Links = load('Links2.txt');
L = load('L2.txt');
nNodes = size(Nodes,1);
nLinks = size(Links,1);

% Problem configuration
n = 10;
Cmax = 1000;

linksCosts = zeros(nNodes,nNodes);
for i = 1:nLinks
    n1 = Links(i, 1);
    n2 = Links(i, 2);
    cost = L(n1, n2);
    linksCosts(n1,n2) = cost;
    linksCosts(n2,n1) = cost;
end

% Graph with costs
G = graph(linksCosts);

nodesDistance = zeros(nNodes, nNodes);
for i = 1:nNodes
    for j = 1:nNodes
        nodesDistance(i,j)= distances(G,i,j);
    end
end

% Output filename
filename = string("optimization_problemn" + n + ".lpt");
file = fopen(filename, 'w');

% Objective function (minimize links)
fprintf(file, 'min\n');
for i = 1:nNodes
    for j = 1:nNodes
        fprintf(file, '+ %d l%d%d ', nodesDistance(i,j) ,i, j);
    end
end

% Constraints
fprintf(file, '\nsubject to\n');

% n servers must be selected
for i = 1:nNodes
    fprintf(file, '+ n%d ', i);
end
fprintf(file, '= %d\n', n);

% One server must be assigned to each node
for i = 1:nNodes
    for j = 1:nNodes
        fprintf(file, '+ l%d%d ', j, i);
    end
    fprintf(file, " = 1\n");
end

% The server assigned to each node must be a server node
for i = 1:nNodes
    for j = 1:nNodes
        fprintf(file, '+ l%d%d - n%d <= 0\n', i, j, i);
    end
end

% Cmax constraint
for i = 1:nNodes
    for j = 1:nNodes
        if (nodesDistance(i,j) > Cmax)
            fprintf(file, '+ n%d + n%d <= 1\n', i, j);
        end
    end
end

% Variables
fprintf(file, '\nbinary\n');
for i = 1:nNodes
    fprintf(file, 'n%d ', i);
end
for i = 1:nNodes
    for j = 1:nNodes
        fprintf(file, 'l%d_%d ', i, j);
    end
end

fprintf(file, '\nend');
fclose(file);