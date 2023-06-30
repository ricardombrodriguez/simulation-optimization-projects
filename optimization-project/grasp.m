
% Initialize graph and its elements
Nodes = load('Nodes2.txt');
Links = load('Links2.txt');
L = load('L2.txt');
nNodes = size(Nodes,1);
nLinks = size(Links,1);
G = graph(L);

% Problem configuration
n = 10;
Cmax = 1000;
nRuns = 10; 
runtimeLimit = 30;
r = 3;

% Stores the objective values of each run [1:n]
objectiveValues = zeros(1, nRuns);

% GRASP algorithm
for run = 1:nRuns

    % To keep track of the run elapsed time
    tic

    % Greedy randomized method
    E = 1:nNodes;
    solution = [];
    
    for iter = 1:n
        R = [];
        for j = E
            [out1,out2] = AverageSP_v2(G, [solution j]);
            if (out2 <= Cmax)
                R = [R; j out1];
            end
        end
        R = sortrows(R, 2);
        e = R(randi(r), 1);  
        solution(iter) = e;
        E = setdiff(E, e);
    end

    % Adaptive search

    improved = true;

    while improved
        currentSolution = solution;
        currentObjective = AverageSP_v2(G, currentSolution);
        improved = false;
        
        for i = 1:n
            for j = setdiff(1:nNodes, currentSolution)
                candidateSolution = currentSolution;
                candidateSolution(i) = j;
                [candidateObjective, maxLenServers] = AverageSP_v2(G, candidateSolution);
                
                if candidateObjective < currentObjective && maxLenServers <= Cmax                         
                    currentSolution = candidateSolution;
                    currentObjective = candidateObjective;
                    improved = true;
                end
            end
        end

        solution = currentSolution;
        
    end

    solutionObjective = AverageSP_v2(G, solution);

    objectiveValues(run) = solutionObjective;

    disp(['best solution for run ', num2str(run)]);
    disp(solution);
    disp(solutionObjective);

    % Check if runtimeLimit is passed
    if toc > runtimeLimit
        disp("ended");
        disp(toc);
        break;
    end

end

% Present results
disp('GRASP Results:');
disp(objectiveValues);
disp('Best Solution Objective Value (Minimum):');
disp(min(objectiveValues));
disp('Average Objective Value:');
disp(mean(objectiveValues));
disp('Worst Solution Objective Value (Maximum):');
disp(max(objectiveValues));