function [out1,out2]= AverageSP_v2(G,servers)
% [out1,out2]= AverageSP_v2(G,servers)
% OUTPUTS:
%   out1 -    average shortest path length from each node to its closest
%             server node (returns -1 for invalid input data)
%   out2 -    maximum shortest path length between server nodes
%             (returns -1 for invalid input data)
% INPUTS:
%   G -       graph of the network
%   servers - a row array with server nodes
    
    nNodes= numnodes(G);
    if length(servers)<1
        out1= -1;
        out2= -1;
        return
    end
    if (max(servers)>nNodes || min(servers)<1 || length(unique(servers))<length(servers))
        out1= -1;
        out2= -1;
        return
    end
    clients= setdiff(1:nNodes,servers);
    dist= distances(G,servers,clients);
    if length(servers)>1
        out1= sum(min(dist))/nNodes;
        out2= max(max(distances(G,servers,servers)));
    else
        out1= sum(dist)/nNodes;
        out2= 0;
    end
end